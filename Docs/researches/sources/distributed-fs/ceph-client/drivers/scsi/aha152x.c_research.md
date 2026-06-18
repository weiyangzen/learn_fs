# sources/distributed-fs/ceph-client/drivers/scsi/aha152x.c

## Purpose
`aha152x.c` is the Linux SCSI host driver for Adaptec AHA-152x and related AIC-6260/AIC-6360/AIC-6370 style ISA or PCMCIA controllers, with additional support for TC1550 register layout quirks and optional ISA PnP/autodetection. It implements host discovery, controller reset, SCSI command queuing, interrupt-driven phase handling, error recovery hooks, BIOS geometry reporting, and proc-style diagnostics for the `aha152x` host template.

## Important APIs, Types, And Functions
The key exported or externally used entry points are `aha152x_probe_one()`, `aha152x_release()`, and `aha152x_host_reset_host()`, which are also declared for the PCMCIA stub in `aha152x.h`. The module entry and exit paths are `aha152x_init()` and `aha152x_exit()`, with `aha152x_setup()` parsing built-in kernel command-line configuration when not built as a module.

`struct aha152x_hostdata` is the central per-host state. It stores the issue, current, disconnected, and done command queues; the host spinlock; current and previous bus state; negotiation state per target; transfer/message buffers; reset delay and configuration flags; selected port windows; and the list node used by the global `aha152x_host_list`. `struct aha152x_cmd_priv`, allocated via the SCSI command private area, tracks per-command data pointer, scatterlist cursor, residual count, status byte, message byte, command-sent flag, and phase flags. `struct aha152x_scdata`, stored in `host_scribble`, links commands in internal queues and holds completion/error-handler save state.

The SCSI mid-layer integration is through `aha152x_driver_template`: `queuecommand`, abort, device reset, bus reset, BIOS geometry, proc show/write callbacks, `cmd_size`, queue depth, SG limits, and DMA boundary. The queue front door is `aha152x_queue_lck()` via `DEF_SCSI_QCMD()`, which calls `aha152x_internal_queue()`.

## Control Flow
Initialization collects setup from command-line/module parameters, optional compile-time `SETUP0/SETUP1`, ISA PnP devices, and BIOS/port probing. `aha152x_probe_one()` allocates the SCSI host, initializes hostdata, programs IDs and options, resets the SCSI bus, resets controller ports, tests the IRQ path using a temporary software interrupt handler, installs the real IRQ handler, adds the host, and scans the bus.

Runtime command flow starts in `aha152x_internal_queue()`, then moves commands from `ISSUE_SC` to `CURRENT_SC`, through selection, message, command, data, status, and bus-free phases. The IRQ handler only schedules work; `is_complete()` performs the actual state-machine loop using `update_state()` and the `states[]` callback table.

## State And Persistence Behavior
Persistent state is in memory only: hostdata queues, per-target synchronous negotiation arrays, current state/previous state, current message buffers, command counters, and optional statistics. Hardware state is held in controller registers, FIFO state, interrupt masks, transfer counters, and SCSI bus signals. No on-disk persistence exists.

## Dependencies And Integration Points
The driver depends on Linux SCSI mid-layer APIs, SPI transport helper `spi_populate_sync_msg()`, ISA/ISAPnP resource APIs, IRQ/workqueue APIs, `scsicam_bios_param()`, and low-level port I/O. It directly includes `aha152x.h` for register layout and bit definitions. It integrates with PCMCIA via non-static probe/release/reset helpers and with module/kernel boot configuration via module parameters and `__setup`.

## Risks
The phase engine is timing-sensitive and depends on correct hardware interrupt, FIFO, and SCSI phase behavior. Several paths call `panic()` through `aha152x_error()` for internal state corruption. `aha152x_abort()` only handles not-yet-issued commands, leaving active or disconnected aborts to fail. Data in/out loops poll with long timeouts and use manual residual repair, so FIFO count mismatches can stall or produce noisy diagnostics. The global `aha152x_tq` work item and global host list require careful lifetime handling when multiple hosts and removal interact.

## Test Signals
Meaningful test signals include successful module load with valid parameters, IRQ software-interrupt self-test success, `scsi_add_host()` and `scsi_scan_host()` success, simple INQUIRY/READ/WRITE completions, disconnect/reconnect behavior, SDTR negotiation, check-condition/request-sense recovery, abort/reset return codes, and proc output from `aha152x_show_info()`.
