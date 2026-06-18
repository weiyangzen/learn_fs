# Research Report: subset-b-004433

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_cmd.h

## Purpose

`hclge_cmd.h` is the PF-side firmware command ABI header for the HNS3 `hclge` Ethernet driver. It does not implement command submission itself, but it defines the descriptor payload layouts, bit positions, limits, and helper aliases used by `hclge_main.c`, traffic management, DCB, debugfs, devlink-adjacent feature queries, and error handling. The common command transport is delegated to `hclge_comm_cmd.h`, with `hclge_cmd_setup_basic_desc()` mapped to the common helper and `hclge_cmd_send()` declared for PF command submission.

## Important APIs, Types, And Constants

The header declares `int hclge_cmd_send(struct hclge_hw *hw, struct hclge_desc *desc, int num)` and a large set of command payload structs. Key groups include queue and interrupt mapping (`hclge_tqp_map_cmd`, `hclge_ctrl_vector_chain_cmd`, `hclge_misc_vector`), packet buffer and waterline configuration (`hclge_tx_buff_alloc_cmd`, `hclge_rx_priv_buff_cmd`, `hclge_pkt_buf_alloc`, `hclge_rx_com_wl_buf_cmd`, `hclge_rx_pkt_buf_cmd`), PF/VF resource discovery (`hclge_func_status_cmd`, `hclge_pf_res_cmd`, `hclge_cfg_param_cmd`, `hclge_vf_num_cmd`), RSS and link status masks, MAC mode/speed/FEC/SFP structures, MAC/VLAN table commands, VLAN filter/offload commands, TSO/GRO and reset payloads, loopback and LED commands, Flow Director TCAM/action/counter payloads, SFP EEPROM multi-BD layout, device specs, PHY settings, and Wake-on-LAN commands.

Most multi-byte fields use `__le16`, `__le32`, or `__le64`, making the file part of the hardware ABI rather than a host-native in-memory contract. Many `*_B`, `*_S`, and `*_M` constants encode bit indices, shifts, and masks consumed through `hnae3_get_bit()`, `hnae3_get_field()`, `hnae3_set_bit()`, and similar helpers.

## Control Flow And Integration

The typical caller flow is: allocate or stack-create one or more `struct hclge_desc`, call `hclge_cmd_setup_basic_desc(desc, opcode, is_read)`, cast `desc.data` to one of these request/response structs, fill fields using CPU-to-little-endian conversions, optionally set `HCLGE_COMM_CMD_FLAG_NEXT` across a descriptor chain, and call `hclge_cmd_send()`. Read paths reverse the process with little-endian conversions after firmware updates descriptor data.

This header is included by `hclge_main.h`, `hclge_debugfs.h`, `hclge_regs.c`, PTP code, and error/debug paths. Debugfs and error handlers depend heavily on these layouts for register dumps, VLAN diagnostics, Flow Director inspection, and MAC tunnel interrupt handling.

## State And Persistence Behavior

The file itself has no persistent state. It defines the exact payloads used to move state between driver memory, firmware command queues, and hardware. Persistent driver effects occur in callers when firmware accepts configuration commands: queue maps, VLAN rules, MAC modes, traffic buffers, FEC modes, reset state, Flow Director rules, and WOL settings can survive beyond a single function call until reset or reconfiguration.

## Dependencies

Dependencies are Linux kernel base types, MMIO annotations, Ethernet helpers, `hnae3.h`, and the shared HNS3 command layer in `hclge_comm_cmd.h`. Correctness also depends on firmware opcode definitions and descriptor data size from the common command header.

## Risks

The highest risk is ABI drift: changing structure layout, field order, reserved padding, endian annotations, or bit constants can silently corrupt firmware commands. Several structures assume descriptor payload size constraints, so additions must account for the 24-byte descriptor data area and multi-BD chains. Bitfield use in `hclge_qos_pri_map_cmd` lives in `hclge_debugfs.h`, but this header also exposes many byte-level flags where host endianness and hardware documentation must be kept aligned. Command structs with `#pragma pack(1)` around `hclge_mac_ethertype_idx_rd_cmd` require special care because packing state can affect later definitions if not restored.

## Test Signals

Useful signals include successful driver probe and reset, `ethtool` link/FEC/WOL operations, VLAN add/delete and offload behavior, RSS and queue mapping validation, DCB/mqprio reconfiguration, Flow Director rule insertion and counter reads, SFP EEPROM reads, and debugfs register dumps that use the same payloads. Kernel sparse/endian checks are important because the header relies on explicit little-endian fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.c

## Purpose

`hclge_dcb.c` implements PF Data Center Bridging support for the HNS3 driver. It bridges Linux DCBNL IEEE ETS/PFC/app callbacks and `tc mqprio` offload into the driver's traffic-manager state (`hdev->tm_info`) and hardware programming. The file is compiled when `CONFIG_HNS3_DCB` is enabled and installs `hnae3_dcb_ops` for PF vport 0 only.

## Important APIs And Functions

The exported entry point is `hclge_dcb_ops_set()`, which checks `hnae3_dev_dcb_supported(hdev)` and PF vport identity, then sets `vport->nic.kinfo.dcb_ops` and initializes `hdev->dcbx_cap` to IEEE host-managed DCBX.

DCBNL callbacks include `hclge_ieee_getets()`, `hclge_ieee_setets()`, `hclge_ieee_getpfc()`, `hclge_ieee_setpfc()`, `hclge_ieee_setapp()`, `hclge_ieee_delapp()`, `hclge_getdcbx()`, and `hclge_setdcbx()`. `hclge_setup_tc()` implements hardware-offloaded `mqprio` channel mode. Helper functions translate between `struct ieee_ets` and TM state, validate TC counts and priority maps, recalculate PFC maps, synchronize mqprio options into `struct hnae3_tc_info`, and reconfigure hardware with `hclge_map_update()`.

## Control Flow

ETS set flow validates DCBX mode and rejects changes while mqprio is active. `hclge_ets_validate()` derives TC count from `prio_tc`, ensures it is within `tc_max` and allocated TQPs, validates SP versus ETS scheduling, rejects ETS bandwidth on disabled TCs, requires nonzero ETS weights, and enforces total ETS bandwidth of 100 percent when any ETS TC exists. If the priority-to-TC map or TC count changes, the driver notifies the NIC client down and uninit, updates TM scheduling information, applies ETS to TM fields, reprograms TM, pause, buffer allocation, RSS indirection, and RSS hardware, then notifies init and up. If only DWRR weights change, it programs `hclge_tm_dwrr_cfg()`.

PFC set flow computes hardware PFC TC bitmap from user priorities and current priority-to-TC mapping, updates `tm_info.hw_pfc_map` and `tm_info.pfc_en`, refreshes TM PFC state, reprograms pause, brings the client down, flushes TM, reallocates buffers, unflushes TM, and brings the client up. DSCP app set/delete maintains `h->kinfo.dscp_prio[]`, calls kernel `dcb_ieee_setapp()` or `dcb_ieee_delapp()`, updates DSCP-to-TC mapping in hardware, and switches `tc_map_mode` between DSCP and priority mapping.

`hclge_setup_tc()` rejects changes before NIC registration and while DCB ETS is active. It validates queue counts as powers of two, enforces continuous offsets from zero, rejects unsupported min/max rate settings, applies down/uninit notifications, updates `kinfo->tc_info`, reprograms TC hardware, and rolls back on failures except for mqprio destroy, which is warned as recoverable after reset.

## State And Persistence Behavior

The file mutates `hdev->tm_info`, `hdev->dcbx_cap`, `vport->nic.kinfo.tc_info`, `vport->nic.kinfo.tc_map_mode`, `h->kinfo.dscp_prio[]`, and `h->kinfo.dscp_app_cnt`. Hardware persistence is through TM scheduler, pause, buffer, RSS, DSCP map, and priority map commands. Client notification ordering protects queue/ring state by taking networking down before major TC map changes and bringing it up afterward.

## Dependencies And Integration Points

It depends on `hclge_main.h`, `hclge_tm.h`, `hclge_dcb.h`, DCBNL IEEE types, Linux `dcb_ieee_*` helpers, and HNS3 client notification callbacks. Probe calls `hclge_dcb_ops_set()` from `hclge_main.c`. DCB operations interact with RSS, pause configuration, TM flush, buffer allocation, MAC stats, PFC stats, and netdev debug logging.

## Risks

Risk concentrates around partial reconfiguration. Several flows update software state before all hardware steps succeed, so rollback coverage matters. PFC set returns the last bad error after attempting cleanup, but `tm_info.pfc_en` remains updated even if later hardware operations fail. ETS map changes rely on down/uninit and init/up notifications; missed notification errors can leave client and hardware state out of sync. DSCP app operations must roll back both kernel DCB app tables and driver arrays when hardware mapping fails. mqprio destroy has an explicit nonfatal failure path where reset is expected to restore state.

## Test Signals

Exercise `dcb` or `lldptool` IEEE ETS/PFC get and set, invalid bandwidth totals, invalid priority-to-TC maps, mqprio activation and destruction, DSCP app add/delete, PFC statistics reads, and reset after DCB changes. Watch for netdev down/up notification errors, traffic continuity across TC reconfiguration, RSS queue distribution after TC count changes, and buffer allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.h

## Purpose

`hclge_dcb.h` is the compile-time gate for HNS3 PF DCB support. It exposes `hclge_dcb_ops_set()` to the main PF driver when `CONFIG_HNS3_DCB` is enabled and provides an empty inline stub otherwise.

## Important API

The only API is `void hclge_dcb_ops_set(struct hclge_dev *hdev)`. With DCB enabled, the implementation in `hclge_dcb.c` installs IEEE DCB and mqprio operations on the PF netdev private info. With DCB disabled, calls compile away through the static inline stub.

## Control Flow And State

The header itself contains no runtime control flow beyond preprocessor selection and no persistent state. Its effect is to keep `hclge_main.c` simple: probe can call `hclge_dcb_ops_set(hdev)` unconditionally while the build configuration determines whether DCB operations are actually attached.

## Dependencies And Integration Points

It includes `hclge_main.h` for `struct hclge_dev`. The integration point is driver initialization in `hclge_main.c`; the operation table installed by the real implementation is later consumed by the HNAE3/netdev DCB path.

## Risks

The main risk is build-configuration divergence. DCB userspace operations silently disappear when `CONFIG_HNS3_DCB` is disabled, so tests must cover both configurations. Because the disabled stub has no logging, feature absence is visible only through missing DCB ops or userspace capability checks.

## Test Signals

Build with `CONFIG_HNS3_DCB=y` and verify DCBNL callbacks are present, then build with it disabled and verify probe still succeeds and DCB operations are absent without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.h

## Purpose

`hclge_debugfs.h` defines PF debug command support types and constants shared by `hclge_debugfs.c` and error logging. It describes management-table decoding masks, DFX BD-number offsets, compact firmware response layouts, formatting lengths, and the exported helper for indexed debug command reads.

## Important Types And Constants

Management table masks decode VLAN, MAC, EtherType, egress type, PF/VF ID, queue, and drop fields. DFX offsets identify firmware-reported BD counts for BIOS, SSU, IGU, RPU, NCSI, RTC, PPP, RCB, TQP, and SSU_2 register groups. `struct hclge_qos_pri_map_cmd` models packed 4-bit priority-to-TC fields. `struct hclge_dbg_bitmap_cmd` provides byte and bitfield views for status bytes. `struct hclge_dbg_reg_common_msg`, `hclge_dbg_tcam_msg`, `hclge_dbg_dfx_message`, `hclge_dbg_reg_type_info`, and `hclge_dbg_func` drive table-based debug dispatch and register printing. `struct hclge_dbg_vlan_cfg` is a normalized aggregate of VLAN TX/RX offload state.

The declared API is `hclge_dbg_cmd_send(struct hclge_dev *hdev, struct hclge_desc *desc_src, int index, int bd_num, enum hclge_opcode_type cmd)`.

## Control Flow And State

The header has no runtime state. Its structures shape how `hclge_debugfs.c` builds descriptor chains, labels DFX outputs, picks read callbacks, and formats debug information into buffers or `seq_file` output.

## Dependencies And Integration Points

It includes `linux/etherdevice.h` and `hclge_cmd.h`, so it inherits the command descriptor ABI. `hclge_err.h` includes this header because error logging reuses debug command helpers for module register dumps.

## Risks

The bitfield layout in `hclge_qos_pri_map_cmd` and `hclge_dbg_bitmap_cmd` is compact but compiler-layout-sensitive, so it should stay aligned with how firmware returns byte-oriented fields on supported architectures. Formatting length constants must be large enough for all strings in the static tables. DFX offset constants must match firmware query order or debug register dumps will request the wrong BD counts.

## Test Signals

Compile with sparse and multiple compiler versions, exercise QoS priority map, DFX register, VLAN, and error-module debug paths, and compare printed field names/counts with firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.c

## Purpose

`hclge_devlink.c` registers minimal devlink support for the HNS3 PF driver. It exposes running firmware version information and supports `DEVLINK_RELOAD_ACTION_DRIVER_REINIT`, mapping devlink reload to the driver's NIC client down/uninit and init/up notification sequence.

## Important APIs And Functions

`hclge_devlink_init()` allocates a devlink instance with `hclge_devlink_ops`, stores `hdev` in private devlink data, assigns `hdev->devlink`, and registers the instance. `hclge_devlink_uninit()` unregisters and frees it.

`hclge_devlink_info_get()` formats `hdev->fw_version` into a four-component string and publishes it as `DEVLINK_INFO_VERSION_GENERIC_FW`. For device revisions newer than V2, it calls `hclge_devlink_scc_info_get()`, which queries SCC firmware version with `hclge_query_scc_version()` and publishes it as `"fw.scc"`.

Reload callbacks are `hclge_devlink_reload_down()` and `hclge_devlink_reload_up()`. Both support only `DEVLINK_RELOAD_ACTION_DRIVER_REINIT`; unsupported actions return `-EOPNOTSUPP`.

## Control Flow

Reload down first rejects operation while `HCLGE_STATE_RST_HANDLING` is set. For driver reinit it takes `rtnl_lock()`, calls the NIC client's `reset_notify()` with `HNAE3_DOWN_CLIENT`, then `HNAE3_UNINIT_CLIENT`, and releases RTNL. Reload up sets `*actions_performed = BIT(action)`, takes RTNL, sends `HNAE3_INIT_CLIENT`, then `HNAE3_UP_CLIENT`, and releases RTNL. Errors short-circuit after unlocking.

## State And Persistence Behavior

Devlink private state is just `struct hclge_devlink_priv { struct hclge_dev *hdev; }`. Runtime effects are on the NIC client and netdev lifecycle through reset notifications. Firmware version strings are read-only snapshots. The devlink pointer persists in `hdev->devlink` until uninit.

## Dependencies And Integration Points

The file depends on Linux devlink, `hclge_devlink.h`, `hclge_main.h` through that header, firmware version macros, `hclge_query_scc_version()`, PCI device revision, `hdev->nic_client`, and HNAE3 reset notification enums. Probe and remove in `hclge_main.c` call the init/uninit functions.

## Risks

`hclge_devlink_uninit()` assumes `hdev->devlink` is valid. Reload paths assume `hdev->nic_client` and its reset callbacks are present and safe under RTNL. The reload implementation handles only client notifications; it does not re-run full hardware probe, so expectations must match devlink's driver-reinit semantics. Formatting uses `%lu` for extracted fields from a `u32`, relying on macro return typing.

## Test Signals

Use `devlink dev info` to verify generic firmware and SCC version fields. Use `devlink dev reload ... action driver_reinit` and confirm down/uninit/init/up notifications, no reload during reset handling, correct `actions_performed`, and no RTNL lock imbalance on callback failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.h

## Purpose

`hclge_devlink.h` declares the HNS3 PF devlink integration points and private devlink storage. It is a small bridge between `hclge_main.c` and `hclge_devlink.c`.

## Important API And Types

`HCLGE_DEVLINK_FW_SCC_LEN` sizes the SCC firmware version string buffer. `struct hclge_devlink_priv` stores the owning `struct hclge_dev *`. The exported functions are `int hclge_devlink_init(struct hclge_dev *hdev)` and `void hclge_devlink_uninit(struct hclge_dev *hdev)`.

## Control Flow And State

The header has no runtime control flow. Its private structure is allocated inside devlink private memory and used by devlink callbacks to recover the PF device pointer.

## Dependencies And Integration Points

It includes `hclge_main.h` for `struct hclge_dev`. `hclge_main.c` calls the declared functions during probe/remove, and devlink callbacks in `hclge_devlink.c` use the private structure.

## Risks

The header assumes devlink support is available through the broader build context. Any change to private data must stay synchronized with `devlink_alloc()` sizing in `hclge_devlink.c`.

## Test Signals

Build the PF driver with devlink enabled, verify probe allocates/registers devlink, remove unregisters/frees it, and devlink callbacks can safely dereference `priv->hdev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.c

## Purpose

`hclge_err.c` implements PF hardware error interrupt configuration, detection, logging, clearing, and reset escalation for HNS3. It covers common HNS blocks, MAC tunnel interrupts, MSI-X reported errors, RAS nonfatal errors, RoCEE RAS errors, firmware-summarized all-error logs, and VF queue-error recovery.

## Important APIs, Tables, And Functions

The exported functions are `hclge_config_mac_tnl_int()`, `hclge_config_nic_hw_error()`, `hclge_config_rocee_ras_interrupt()`, `hclge_handle_hw_ras_error()`, `hclge_handle_hw_msix_error()`, `hclge_handle_mac_tnl()`, `hclge_handle_all_hns_hw_errors()`, `hclge_find_error_source()`, `hclge_handle_occurred_error()`, `hclge_handle_error_info_log()`, and `hclge_handle_vf_queue_err_ras()`.

Large `hclge_hw_error` tables map interrupt status masks to log strings and reset levels for IMP TCM, CMDQ, TQP, MSI-X SRAM, IGU/EGU, NCSI, PPP, TM, QCN, MAC AFIFO/TNL, PPU, SSU, and RoCEE overflow conditions. Module/type tables decode firmware all-error summaries into human-readable module and error-type names. Register-info tables describe extra SSU/IGU/RPU/general DFX registers printed when certain module errors occur.

## Control Flow

Enable/disable flow starts at `hclge_config_nic_hw_error()`: it toggles vector0 all-MSI-X error delivery through MMIO, then iterates `hw_blk[]` and calls per-block command functions to configure IGU/EGU, PPP, SSU, PPU, TM, COMMON, and MAC error interrupts. `hclge_config_rocee_ras_interrupt()` separately handles RoCEE on supported V2+ RoCE devices and clears pending RoCEE RAS state when enabling.

RAS handling starts in `hclge_handle_hw_ras_error()`. It refuses recovery before service initialization, reads `HCLGE_RAS_PF_OTHER_INT_STS_REG`, clears `ae_dev->hw_err_reset_req` for relevant nonfatal bits, handles HNS RAS via `hclge_handle_all_ras_errors()`, handles RoCEE RAS via `hclge_handle_rocee_ras_error()`, and returns `PCI_ERS_RESULT_NEED_RESET` if any reset bit was requested. HNS RAS handling queries firmware-reported MPF/PF BD counts, allocates descriptors, reads and logs MPF and PF RAS registers, sets reset bits from tables, reports selected hardware errors, and reuses the descriptors to clear interrupts.

MSI-X handling starts in `hclge_handle_hw_msix_error()`, which requires service initialization and then queries MPF/PF BD counts. MPF MSI-X handling logs MAC AFIFO/TNL and selected PPU errors; PF MSI-X handling logs SSU, PPP, and PPU PF errors and treats `over_8bd_no_fe` specially by querying vport/queue details and requesting either VF notification or PF reset. Both paths clear their interrupt status through `hclge_clear_hw_msix_error()`, then `hclge_handle_mac_tnl()` records MAC tunnel interrupt status and time into `hdev->mac_tnl_log`.

`hclge_handle_error_info_log()` queries firmware's all-error BD count and data, converts descriptor data to CPU-endian words, decodes nested summary/module/type/register records, logs register values, optionally queries extra module registers, sets reset bits, and marks `HNAE3_VF_EXP_RESET` when supported VF-caused errors are detected. `hclge_handle_vf_queue_err_ras()` consumes that VF reset request, queries a VF fault bitmap, resets TQPs, informs affected VFs, and clears broader reset requests if VF-local recovery succeeded.

## State And Persistence Behavior

The file mutates `ae_dev->hw_err_reset_req`, hardware interrupt enable registers, hardware interrupt status through query-clear commands, `hdev->mac_tnl_log`, and VF reset state through mailbox/reset notification helpers. Error logs persist only through kernel logs and debugfs-visible MAC tunnel FIFO entries. Reset request bits persist until consumed by the reset/service path.

## Dependencies And Integration Points

It depends on command descriptors, debug command send support, HNS3 MMIO helpers, PCI error recovery types, RoCE capability checks, reset notification helpers, VF/vport helpers, and HNAE3 reset enums. `hclge_main.c` enables NIC hardware errors during initialization and reset recovery, disables them during teardown, invokes MSI-X/RAS handlers from service or interrupt paths, and exposes `handle_hw_ras_error` through AE ops.

## Risks

Error decoding is highly firmware-layout-dependent: descriptor indices, status masks, BD minimums, and nested all-error records must match firmware. Several handlers allocate descriptor arrays sized by firmware-reported counts; count validation protects minimums, but unexpectedly large values still create memory pressure. Logging and clearing are coupled: command failures can leave interrupts uncleared and retriggering. Some errors request global reset while others request function or VF reset; incorrect table reset levels can either over-reset or under-recover. VF-local recovery relies on accurate bitmaps and valid vport lookup. `hclge_handle_error_type_reg_log()` indexes module/type tables through sentinel-like defaults, so unknown module/type combinations need careful bounds behavior.

## Test Signals

Test interrupt enable/disable command payloads, service-init gating, RAS and MSI-X query-clear failure paths, firmware-reported invalid BD counts, RoCEE AXI/ECC/overflow logs, `over_8bd_no_fe` PF versus VF handling, all-error summary parsing with malformed lengths, VF fault bitmap recovery, MAC tunnel FIFO logging, and reset request bit outcomes. Fault-injection or firmware command mocking is needed for meaningful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.h

## Purpose

`hclge_err.h` is the public and shared definition header for HNS3 PF hardware error handling. It declares interrupt masks, status masks, descriptor limits, module/type identifiers, error logging structures, module register dump descriptors, and the functions used by `hclge_main.c` and related PF subsystems to configure and handle hardware errors.

## Important Types And Constants

The header defines minimum BD counts for MPF/PF RAS and MSI-X status queries, RAS status register addresses and masks, vector0 MSI-X masks, per-block interrupt enable and mask constants for COMMON, IGU/EGU, PPP, TM/QCN, NCSI, MAC, PPU, SSU, and RoCEE, plus descriptor and register-list sizing limits. `enum hclge_err_int_type` classifies MSI-X and RAS CE/NFE/FE categories. `enum hclge_mod_name_list` and `enum hclge_err_type_list` encode firmware module and error type IDs for all-error logs.

Core structures include `hclge_hw_blk` for configurable error blocks, `hclge_hw_error` for status-bit to message/reset mappings, `hclge_hw_module_id` and `hclge_hw_type_id` for all-error summary decoding, `hclge_sum_err_info`, `hclge_mod_err_info`, and `hclge_type_reg_err_info` for firmware log records, and `hclge_mod_reg_info` plus `hclge_mod_reg_common_msg` for follow-up DFX register queries.

## Exported APIs

The declared APIs configure MAC tunnel interrupts, NIC hardware error interrupts, and RoCEE RAS interrupts; handle all HNS hardware errors during init; locate and process occurred errors; process PCI RAS and MSI-X hardware error paths; log firmware all-error info; handle MAC tunnel interrupts; and perform VF queue-error RAS recovery.

## Control Flow And State

The header itself has no runtime control flow, but its constants determine which bits are enabled, queried, logged, cleared, or converted into reset requests by `hclge_err.c`. Its firmware record structures define the in-memory overlay used when descriptor data is decoded.

## Dependencies And Integration Points

It includes `hclge_main.h`, `hclge_debugfs.h`, and `hnae3.h`. This ties error handling to the PF device state, debug command helpers for module register dumps, and HNAE3 reset/error enums. `hclge_main.c` and AE ops use the function declarations directly.

## Risks

Because this header mirrors hardware and firmware contracts, mask mistakes can enable the wrong interrupt, fail to clear a source, or misclassify reset severity. Descriptor size constants must match command queue payload layout. Firmware all-error structures are compact and interpreted from raw `u32` buffers; field order and maximum register count are critical. Including `hclge_debugfs.h` creates a coupling from error handling to debug helper declarations.

## Test Signals

Build coverage should include sparse/endian checks and all supported device revisions. Runtime tests should validate interrupt masks against firmware documentation, all-error log decoding, RoCEE capability gating, VF fault support gating, and reset-level propagation from `hclge_hw_error` tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_err.h -->
