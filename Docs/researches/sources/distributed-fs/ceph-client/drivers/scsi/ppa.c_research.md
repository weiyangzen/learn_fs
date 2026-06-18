# sources/distributed-fs/ceph-client/drivers/scsi/ppa.c

## Purpose
`ppa.c` is the low-level SCSI host adapter driver for the Iomega PPA3 parallel-port SCSI interface used by ZIP drives. It registers as a parport driver, probes compatible ports/devices, exposes one SCSI host per attached adapter, and runs a polled phase engine because the hardware does not provide normal interrupts.

## Important APIs, types, and functions
The central soft state is `ppa_struct`, which stores the parport device, base I/O port, selected transfer mode, current SCSI command, delayed work item, timeout/reconnect parameters, parport wait state, SCSI host pointer, and list node. Important parport helpers are `ppa_pb_claim()`, `ppa_pb_dismiss()`, `ppa_pb_release()`, `ppa_wakeup()`, and `got_it()`. Register-transfer helpers include `ppa_wait()`, `epp_reset()`, `ecp_sync()`, `ppa_byte_out()`, `ppa_byte_in()`, `ppa_nibble_in()`, `ppa_out()`, and `ppa_in()`.

Protocol sequencing is implemented by `ppa_connect()`, `ppa_disconnect()`, `ppa_select()`, `ppa_send_command()`, `ppa_completion()`, and `ppa_engine()`. SCSI integration comes from `ppa_template`, `ppa_queuecommand()`, `ppa_abort()`, `ppa_reset()`, and `ppa_biosparam()`. Device discovery and parport lifecycle are handled by `device_check()`, `ppa_init()`, `__ppa_attach()`, `ppa_attach()`, `ppa_detach()`, and `module_parport_driver()`.

## Control flow
When a parport appears, `__ppa_attach()` allocates `ppa_struct`, registers a parport device with a wakeup callback, claims the port, initializes the adapter, chooses I/O port count based on mode, allocates a SCSI host, links the host data back to `ppa_struct`, calls `scsi_add_host()`, and scans. `ppa_init()` autodetects NIBBLE, PS/2, or EPP modes from parport capabilities, performs connect/disconnect handshakes, pulses reset, and calls `device_check()`, which scans SCSI IDs with TEST UNIT READY and can fall back from attempted EPP to the old mode.

`ppa_queuecommand_lck()` accepts only one active command, initializes phase zero and default failure result, schedules delayed work, and attempts to claim the parport. `ppa_interrupt()` repeatedly calls `ppa_engine()`. The engine advances through phases for waiting on parport ownership, cable sanity check, target select, command send, scatterlist setup, data transfer, and final status/message read. `ppa_completion()` moves data in bursts for READ/WRITE commands but yields after about one jiffy to avoid monopolizing CPU. Successful or failed terminal states dismiss the parport and call `scsi_done()`.

## State and persistence behavior
State is in memory and port hardware registers. The driver has no durable persistence. Runtime tunables include the module-level `mode` parameter and proc write support for per-device `mode=` and `recon_tmo=`. The current command is stored in `dev->cur_cmd`, and phase/data-transfer position is held in the command-private `struct scsi_pointer`.

## Dependencies and integration points
The file depends on parport, low-level x86 I/O port helpers via `ppa.h`, delayed work, jiffies/udelay/mdelay timing, SCSI midlayer, scatterlist helpers, and legacy proc host-template hooks. It integrates parport arbitration with SCSI command serialization and uses PPA-specific handshakes to emulate a SCSI bus behind a parallel-port device.

## Risks and test signals
Risks include busy-wait CPU cost, fragile timing with old parallel-port chipsets, single-command serialization, no real abort after SCSI command issue, use of `sg_virt()` requiring CPU-addressable SG memory, EPP timeout handling, and detach while delayed work or `cur_cmd` is live. Useful tests include module load with each mode, autodetection fallback, no-device and cable-unplug paths, READ/WRITE scatterlist transfer across segments, SCSI EH abort/reset behavior, parport sharing contention, and detach/remove with no work left queued.
