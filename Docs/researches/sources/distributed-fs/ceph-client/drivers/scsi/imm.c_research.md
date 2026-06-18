<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/imm.c

## Purpose

`imm.c` is a low-level SCSI host adapter driver for the Iomega MatchMaker parallel-port SCSI interface embedded in ZIP Plus drives. It registers as a parport driver, probes compatible devices, exposes a single-command SCSI host, manually drives parallel-port control/data/status registers, and uses delayed work as a polling engine because the adapter does not provide usable interrupts.

## Important APIs, Types, and Functions

- `imm_struct` is the per-adapter state: parport device, base/base_hi I/O ports, transfer mode, current SCSI command, delayed work, start jiffies, transfer flags, parport arbitration state, device number, waitqueue pointer, SCSI host, and list node.
- Parport arbitration functions are `imm_pb_claim()`, `imm_pb_dismiss()`, `imm_pb_release()`, `imm_wakeup()`, and `got_it()`.
- Register/protocol primitives include `imm_wait()`, `imm_negotiate()`, `epp_reset()`, `ecp_sync()`, `imm_cpp()`, `imm_connect()`, `imm_disconnect()`, and `imm_select()`.
- Data movement helpers are `imm_byte_out()`, `imm_nibble_in()`, `imm_byte_in()`, `imm_out()`, `imm_in()`, and `imm_completion()`.
- SCSI engine and host callbacks include `imm_send_command()`, `imm_engine()`, `imm_interrupt()`, `imm_queuecommand_lck()`, `imm_abort()`, `imm_reset()`, `imm_biosparam()`, `imm_show_info()`, and `imm_write_info()`.
- Probe/remove are implemented by `__imm_attach()`, `imm_attach()`, `imm_detach()`, and `module_parport_driver(imm_driver)`.

## Control Flow

Module load registers a parport driver. On each matching parport, `__imm_attach()` allocates `imm_struct`, registers a parport device callback, claims the parport or waits briefly for ownership, initializes the hardware through `imm_init()`, allocates a SCSI host, stores `imm_struct *` in host private data, adds the host, and scans it.

Command execution starts in `imm_queuecommand_lck()`: it records `cur_cmd`, initializes the private `scsi_pointer` phase to zero, schedules delayed work immediately, and attempts to claim the parport. `imm_interrupt()` repeatedly calls `imm_engine()`; if the engine returns "still working", the delayed work is rescheduled one tick later. When the engine finishes, it disconnects if needed, releases the parport, clears `cur_cmd`, and calls `scsi_done()`.

`imm_engine()` is a phase machine: wait for parport ownership, connect to the MatchMaker interface, select the target SCSI ID, send the CDB in byte pairs, set up the scatterlist cursor, detect data direction and data phase, optionally negotiate IEEE 1284 mode for reads, transfer data in bursts or byte/nibble loops, perform post-data handshakes, read status/message bytes, and set `cmd->result`.

`device_check()` probes SCSI IDs, optionally tries EPP mode first during autodetect, sends Test Unit Ready, falls back to the original mode on failure, and resets/disconnects the device before returning success or probe failure.

## State and Persistence

State is volatile and per adapter. The only user-tunable persistent-for-module state is the `mode` module parameter; `/proc/scsi/imm/N` `write_info` can change `dev->mode` at runtime. `cur_cmd` enforces `can_queue = 1`. The SCSI command private `scsi_pointer` stores phase, SG cursor, residual bytes, and data pointer. No on-disk state is written.

The global `imm_hosts` list assigns stable ascending device numbers during attach and locates devices during detach. `arbitration_lock` protects `wanted` and parport claim state across callback and command contexts.

## Dependencies and Integration Points

The file depends on Linux parport APIs, raw I/O port accessors, delayed work, SCSI midlayer APIs, scatterlist helpers, and the local `imm.h` register/mode macros. It registers `imm_template` with SCSI, including queuecommand, abort, host reset, BIOS geometry, proc show/write hooks, `can_queue = 1`, `sg_tablesize = SG_ALL`, and private command size `sizeof(struct scsi_pointer)`.

## Risks and Edge Cases

- Hardware timing is manual and fragile: many paths use `udelay()`, polling loops, and magic control-register sequences.
- The EPP input path uses word/long I/O depending on mode and alignment; regressions can corrupt data or leave EPP timeout bits set.
- Odd SG residual lengths are rounded up to even bytes to satisfy byte-pair output, which can be surprising near buffer boundaries.
- Abort is only possible before the command reaches the SCSI bus; later aborts fail because the interface ties SCSI_MESSAGE high.
- `imm_completion()` intentionally yields after about one jiffy to avoid monopolizing CPU; changing this affects latency and fairness.
- Probe claims the parport with a bounded wait; ports owned too long cause attach failure.
- Raw port I/O and `base_hi` ECP handling are platform/hardware dependent.
- `/proc` write mode changes have minimal validation beyond string prefix and can switch modes while hardware behavior is marginal.

## Test Signals

Expected signals include successful parport registration, probe messages showing discovered SCSI ID and selected transfer mode, SCSI scan discovering the ZIP device, successful READ/WRITE commands in all supported modes, clean behavior when no device is present, timeout logs from `imm_wait()` on disconnected hardware, abort success only in phases 0-1, host reset pulsing and recovering the device, and detach cancelling delayed work without completing a freed command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.c -->
