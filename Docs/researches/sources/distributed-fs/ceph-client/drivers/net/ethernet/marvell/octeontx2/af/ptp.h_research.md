# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.h

## Purpose
`ptp.h` declares the small RVU-private PTP device state structure and the PTP driver hooks consumed by the RVU Admin Function. It provides the compile unit contract between the PTP PCI side driver in `ptp.c` and the RVU AF lifecycle in `rvu.c`.

## Important APIs, Types, and Functions
- `struct ptp` stores the PTP PCI device, MMIO base, timestamp read callback, timestamp spinlock, CN10K errata hrtimer state, input clock rate, and derived clock period.
- `struct rvu;` is forward-declared so `ptp_start()` can accept an RVU object without including the full RVU definition in every consumer.
- `ptp_get()` returns a referenced PTP block or an error pointer.
- `ptp_put()` drops the PCI device reference acquired by `ptp_get()`.
- `ptp_start()` programs and enables the PTP clock once RVU firmware data is available.
- `extern struct pci_driver ptp_driver` lets `rvu.c` register and unregister the PTP PCI driver as part of the overall AF module lifecycle.

## Control Flow
The header has no executable control flow. Its declarations are used by `rvu_init_module()` to register the PTP PCI driver before the AF driver, by `rvu_probe()` to acquire and start the PTP block, and by `rvu_remove()`/error unwinds to release it. Runtime mailbox PTP operations are implemented in `ptp.c` and declared indirectly through the mailbox handler macro expansion in `rvu.h`, not here.

## State and Persistence Behavior
All state described here is in-memory and device-lifetime scoped. The hardware clock configuration itself lives in PTP CSRs accessed through `reg_base`; the fields in `struct ptp` are cached pointers, callbacks, and timer bookkeeping. There is no persistent storage.

## Dependencies and Integration Points
The header depends on Linux timecounter/time64 declarations, spinlocks, hrtimers through included kernel headers, and PCI types via users including it. It is included by both `ptp.c` and `rvu.h`, and it sits on the boundary between the PTP PCI function and the broader RVU AF driver.

## Risks and Edge Cases
- The header exposes `struct ptp` internals rather than an opaque type, so future consumers could bypass the locking and helper APIs.
- `clock_rate` and `clock_period` are `u32`; this is adequate for current rates used by the driver but should be reviewed if larger external clock rates are introduced.
- Consumers must respect the `ptp_get()`/`ptp_put()` reference contract and must not dereference error pointers.

## Test Signals
- Compile all RVU AF files with this header included in both PTP and non-PTP call sites.
- Static analysis should flag direct `struct ptp` field access outside `ptp.c` if new consumers are added.
- Probe/remove tests should verify reference balance between `ptp_get()` and `ptp_put()`.
