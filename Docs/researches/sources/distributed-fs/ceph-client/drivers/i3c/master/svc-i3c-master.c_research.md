# sources/distributed-fs/ceph-client/drivers/i3c/master/svc-i3c-master.c

## Purpose

`svc-i3c-master.c` implements the Silvaco dual-role I3C master driver, including support for SDR private transfers, limited HDR-DDR transfers, CCCs, DAA, IBI and Hot-Join handling, I2C transfers, runtime PM, and Nuvoton NPCM845-specific hardware quirks.

## Important APIs, Types, and Functions

- Register macros cover master configuration/control/status, interrupt/status bits, IBI rules, error/warning flags, FIFO data/control, dynamic address, and timing fields.
- `struct svc_i3c_master` stores the I3C core object, MMIO regs, saved PM registers, address/descriptor slots, work item for Hot-Join DAA, clocks, transfer queue, IBI slot tracking, global mutex, quirks, enabled event mask, and cached `MCONFIG`.
- Quirks cover FIFO-empty transfer corruption, false `SLVSTART`, and DAA corruption when `SKEW/ODHPP` are both zero.
- `svc_i3c_master_bus_init()` computes `MCONFIG` timing for pure/mixed bus modes, assigns the master dynamic address, and advertises HDR-DDR capability.
- `svc_i3c_master_do_daa_locked()` drives the hardware ProcessDAA sequence, handles IBI arbitration during DAA, prefills dynamic addresses, copes with address NACKs, and returns discovered addresses.
- `svc_i3c_master_xfer()` is the common low-level SDR/I2C/DDR transfer engine.
- IBI functions implement manual ACK/NACK, payload fetch, generic IBI queueing, and Hot-Join work scheduling.

## Control Flow

Probe obtains match data, maps registers, gets clocks and the fast clock, requests the IRQ with `IRQF_NO_SUSPEND`, initializes queues/locks/IBI slots, enables runtime PM, resets the controller, and registers the I3C master. Bus init resumes the device, derives push-pull/open-drain/I2C timing fields from the fast clock and bus mode, writes `MCONFIG`, assigns a master dynamic address, writes `MDYNADDR`, and stores the timing register for later speed changes.

Transfers allocate a flexible `svc_i3c_xfer`, populate one command per requested xfer, serialize through `master->lock`, enqueue under `xferqueue.lock`, and wait for completion. `svc_i3c_master_start_xfer_locked()` executes queued commands synchronously while holding the spinlock, using `svc_i3c_master_xfer()` to emit START/address, handle IBIWON arbitration, handle NACK retry via repeated START, read/write FIFOs, wait for COMPLETE, then emit STOP or DDR force-exit unless the command is continued.

IBI handling starts from `SLVSTART` IRQ. The ISR clears false events, manually emits broadcast address for arbitration, waits for IBIWON, ACKs or NACKs based on IBI type and enabled events, fetches payload into a generic IBI slot, emits STOP, queues the IBI, or schedules Hot-Join DAA work.

## State and Persistence Behavior

Slot allocation is stored in `free_slots`, `addrs[]`, and `descs[]`; per-device private data stores slot index, IBI slot index, and IBI pool. Runtime suspend saves `MCONFIG` and `MDYNADDR`, disables clocks, and selects pinctrl sleep state. Runtime resume restores clocks, pinctrl default, and saved registers if needed. `enabled_events` combines IBI and Hot-Join enable state and controls `SLVSTART` interrupt masking.

## Dependencies and Integration Points

The driver integrates with platform/OF probing, clock and pinctrl PM APIs, runtime PM, I3C master ops, I2C adapter timeout, generic IBI pools, and the I3C core workqueue for Hot-Join DAA. Device-specific quirks are selected by OF match data.

## Risks and Edge Cases

The low-level transfer path polls while holding `xferqueue.lock` with IRQs disabled in several paths, intentionally minimizing IBI arbitration latency but raising latency concerns. DDR support rejects transfers larger than FIFO capacity minus command overhead. `enabled_events++` for IBI enable mixes counter and bitmask semantics with `SVC_I3C_EVENT_HOTJOIN`; this works only if event bits do not conflict with the count range. IBI max payload is limited to FIFO size. DAA intentionally ignores individual `i3c_master_add_i3c_dev_locked()` return values to avoid address reuse hazards.

## Test Signals

Cover timing calculation in all bus modes, `set_speed()` transitions, DAA with NACK/retry and IBIWON arbitration, Nuvoton quirk paths, SDR private multi-transfer continued sequences, I2C repeated starts, DDR size limits and CRC errors, CCC broadcast/direct flows, IBI with and without payload, Hot-Join work scheduling, runtime suspend/resume register restore, and no lockdep/IRQ-latency regressions.
