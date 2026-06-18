# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_cn9k.c

## Purpose
This file implements CN9K/CN93-compatible VF hardware operations for queue register setup, reset, interrupt handling, mailbox register binding, queue enable/disable, register dump, and configuration initialization.

## Important APIs, Types, And Functions
- Debug/reset: `cn93_vf_dump_q_regs()`, `cn93_vf_reset_iq()`, `cn93_vf_reset_oq()`, and `octep_vf_reset_io_queues_cn93()`.
- Config: `octep_vf_init_config_cn93_vf()` reads rings-per-VF from `CN93_VF_SDP_R_IN_CONTROL(0)` and initializes descriptor counts, instruction type, thresholds, and MSI-X count.
- Register setup: `octep_vf_setup_iq_regs_cn93()`, `octep_vf_setup_oq_regs_cn93()`, and `octep_vf_setup_mbox_regs_cn93()`.
- Interrupts: `octep_vf_ioq_intr_handler_cn93()` checks for PF-to-VF mailbox status on queue 0, schedules mailbox work, clears mailbox interrupt status, and schedules NAPI.
- Ops registration: `octep_vf_device_setup_cn93()` populates `struct octep_vf_hw_ops` and calls config init.

## Control Flow
The VF main probe selects this file for CN93/CNF95N/CN98 VF device IDs. Queue setup waits for hardware IDLE bits, programs descriptor base/size registers, configures 64-byte instruction mode and endianness behavior, stores MMIO register pointers in IQ/OQ objects, and sets interrupt thresholds. Open later enables queues and interrupts through the registered ops. Mailbox notifications share queue-0 interrupt delivery: the IOQ handler checks the mailbox interrupt register before scheduling NAPI.

## State And Persistence
Runtime state written by this file includes `oct->conf` queue/MSI-X settings, IQ register pointers, OQ register pointers, mailbox register pointers, hardware ring control, descriptor bases, ring sizes, interrupt thresholds, and enable bits. It does not persist outside hardware registers and the in-memory VF device structure.

## Dependencies And Integration Points
It depends on `octep_vf_regs_cn9k.h` for register definitions, `octep_vf_main.h` for device and ops types, and `octep_vf_config.h` for defaults. It is called by `octep_vf_device_setup()` and used indirectly by `octep_vf_main.c`, `octep_vf_tx.c`, `octep_vf_rx.c`, and `octep_vf_mbox.c` through `hw_ops`.

## Risks And Edge Cases
- Busy-wait loops for IDLE have no explicit timeout; broken hardware can hang setup.
- Queue 0 carries mailbox interrupt side effects; changes to queue interrupt routing must preserve mailbox handling.
- Register reset writes broad masks to doorbell/count registers and must match hardware clear semantics.
- Configuration trusts the rings-per-VF field read from hardware; invalid zero or too-large values would affect allocation and MSI-X setup.

## Test Signals
Probe CN93/CNF95N/CN98 VFs, verify ring count discovery, open/stop queues, send Tx/Rx traffic, receive PF-to-VF link notifications on queue 0, inspect register dumps, test interrupt enable/disable, and run reset/reopen loops.
