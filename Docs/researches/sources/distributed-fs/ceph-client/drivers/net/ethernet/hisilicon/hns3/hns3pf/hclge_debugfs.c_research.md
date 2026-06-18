# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.c

## Purpose

`hclge_debugfs.c` supplies the PF implementation behind HNS3 debug commands. It maps `enum hnae3_dbg_cmd` values to `seq_file` read callbacks that dump hardware registers, traffic-manager state, QoS/DCB configuration, MAC/VLAN/Flow Director tables, reset/service counters, interrupt resources, firmware IMP/NCL data, loopback status, PTP state, and UMV/MAC list information. It is diagnostic code, but it exercises many live firmware command paths.

## Important APIs, Tables, And Handlers

The externally visible functions are `hclge_dbg_get_read_func()`, `hclge_dbg_cmd_send()`, and `hclge_dbg_dump_rst_info()`. `hclge_dbg_cmd_func[]` is the main dispatch table from `HNAE3_DBG_CMD_*` to `read_func` callbacks. `hclge_dbg_reg_info[]` maps DFX register dump commands to firmware opcodes, BD-number offsets, and register-name tables.

Large static `hclge_dbg_dfx_message` arrays describe BIOS common, SSU, IGU/EGU, RPU, NCSI, RTC, PPP, RCB, and TQP register fields. Handler families include MAC register reads, DCB internal status, generic DFX register dumping, TC/TM node/shaper/map reads, QoS pause/priority/DSCP/buffer dumps, management table reads, Flow Director TCAM and counters, reset and service info, IMP stats, NCL config, loopback, MAC tunnel interrupt history, UC/MC MAC list dumps, UMV usage, VLAN filter/offload config, and PTP diagnostics.

## Control Flow

Debugfs lookup calls `hclge_dbg_get_read_func(handle, cmd, &func)`, which searches `hclge_dbg_cmd_func[]` and returns the matching callback or `-EINVAL`. Most callbacks obtain `struct hclge_dev` from the `seq_file` through `hclge_seq_file_to_hdev()`. Hardware-backed dumps create command descriptors, call `hclge_cmd_setup_basic_desc()`, optionally chain descriptors with `HCLGE_COMM_CMD_FLAG_NEXT`, issue `hclge_cmd_send()` or `hclge_dbg_cmd_send()`, convert little-endian descriptor data, and print with `seq_printf()`.

Register DFX dumps first query descriptor counts with `hclge_dbg_get_dfx_bd_num()`. TQP register dumps loop over allocated TQPs; common dumps issue one indexed query. TM and DCB dumps often call `hclge_tm_get_*()` helpers rather than hand-decoding raw descriptors. Flow Director TCAM dumping snapshots rule locations under `fd_rule_lock`, then reads X and Y TCAM banks with a three-descriptor command. VLAN config loops over PF plus enabled VFs and reads TX/RX offload and filter state. MAC tunnel debug output drains `hdev->mac_tnl_log` with `kfifo_get()`.

## State And Persistence Behavior

Most handlers are read-only from a device configuration perspective, but several have stateful observation side effects. `hclge_dbg_dump_mac_tnl_status()` consumes entries from the MAC tunnel log FIFO, so repeated reads can change visible history. FD rule location collection is protected by `fd_rule_lock`; MAC list iteration uses each vport's `mac_list_lock`; UMV share counts use `vport_lock`. Reset and service dumps read live counters and registers. Firmware debug reads may clear nothing by themselves, but they depend on command queue availability and current hardware state.

## Dependencies And Integration Points

The file depends on command ABI definitions from `hclge_cmd.h`, error declarations for reset/error state, `hclge_regs.h` for DFX BD count support, `hclge_tm.h` for traffic-manager queries, PTP helpers, kernel `seq_file`, `kfifo`, local clock, and string choice helpers. `hclge_main.c` exposes `hclge_dbg_get_read_func` in the AE ops table and uses `hclge_dbg_dump_rst_info()` for reset diagnostics.

## Risks

Diagnostic reads can be expensive: TQP, queue, qset, VLAN, and register dumps loop over hardware resources and issue many firmware commands. Some handlers return on the first firmware error, producing partial output. Output format is manually aligned and can break userspace parsers if changed. Bounds depend on firmware-reported BD counts and local message-table sizes; the code uses `min_t()` for DFX dumps but still allocates descriptor arrays sized by firmware. `hclge_dbg_get_rules_location()` treats a mismatch between list count and `hclge_fd_rule_num` as `-EINVAL`, which can race with rule updates if locking expectations change. PTP dump assumes `hdev->ptp` is valid for the command path. MAC tunnel debug draining the FIFO is a notable observability side effect.

## Test Signals

Run every `HNAE3_DBG_CMD_*` path on supported hardware or a command-mocking harness. Validate unsupported cases for non-DCB and non-FD devices return `-EOPNOTSUPP`. Check memory allocation failures for dynamic BD arrays, firmware command failure propagation, concurrent FD rule and MAC list updates, large TQP counts, VLAN output with enabled VFs, and repeated MAC tunnel status reads. Sparse/endian checks should cover descriptor casts and little-endian conversions.
