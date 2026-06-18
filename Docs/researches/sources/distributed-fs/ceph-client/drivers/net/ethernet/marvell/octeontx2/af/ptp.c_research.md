# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.c

## Purpose
`ptp.c` implements the Marvell OcteonTX2/CN10K PTP PCI function used by the RVU Admin Function driver. It maps the PTP CSR BAR, enables and calibrates the hardware PTP clock, exposes clock read/adjust/PPS/timestamp operations through RVU mailbox handlers, and handles CN10K A0/A1 errata for nanosecond rollover and PPS threshold programming. It is not a Linux `ptp_clock_info` provider by itself in this file; instead, AF consumers reach it through `rvu_mbox_handler_ptp_op()` and `rvu_mbox_handler_ptp_get_cap()`.

## Important APIs, Types, and Functions
- Device matching is driven by `ptp_id_table` and the exported `struct pci_driver ptp_driver`.
- `ptp_probe()` allocates `struct ptp`, enables the PCI function, maps BAR0, initializes the spinlock and errata-specific timestamp reader, and records the first discovered block in `first_ptp_block`.
- `ptp_get()` and `ptp_put()` are the RVU side acquisition/release hooks; they detect absent hardware, probe deferral, and failed PTP probe state.
- `ptp_start()` programs clock source selection, timestamp input configuration, rollover registers, PTP enable, atomic set operation, and `PTP_CLOCK_COMP`.
- `ptp_adjfine()` updates frequency compensation from scaled ppm, with an errata-specific recalculation path through `ptp_calc_adjusted_comp()`.
- `ptp_atomic_update()` and `ptp_atomic_adjtime()` use CN10K atomic set/inc/dec CSRs when supported.
- `ptp_pps_on()`, `ptp_set_thresh()`, `ptp_config_hrtimer()`, and `ptp_reset_thresh()` configure PPS output and work around older CN10K threshold timing.
- `ptp_get_clock()` reads the running PTP clock; `ptp_get_tstmp()` reads an external timestamp capture register, with CN10K A-format unpacking.
- `rvu_mbox_handler_ptp_op()` dispatches mailbox operations such as `PTP_OP_ADJFINE`, `PTP_OP_GET_CLOCK`, `PTP_OP_GET_TSTMP`, `PTP_OP_SET_THRESH`, `PTP_OP_PPS_ON`, `PTP_OP_ADJTIME`, and `PTP_OP_SET_CLOCK`.

## Control Flow
Module initialization in `rvu.c` registers `ptp_driver` before the RVU AF driver. When the PTP PCI function probes, `ptp_probe()` maps the register window and stores a global pointer. Later, `rvu_probe()` calls `ptp_get()` and keeps the pointer in `rvu->ptp`; after firmware data is mapped, `ptp_start()` receives the system clock, optional external clock rate, and external timestamp GPIO selector from `rvu->fwdata`.

At runtime, PF/VF drivers send PTP mailbox requests to AF. `rvu_mbox_handler_ptp_op()` validates that `rvu->ptp` exists, then calls the local helper for the requested operation. Clock reads use the function pointer set at probe: old CN10K errata silicon reads seconds and nanoseconds under `ptp_lock` and compensates for rollover; other devices read the nanosecond counter directly. Frequency adjustment computes a fixed-point compensation value and writes `PTP_CLOCK_COMP`. Clock set and adjustment use the atomic timestamp registers; sub-second deltas use hardware increment/decrement while larger deltas compute a replacement timestamp.

PPS enable writes PPS threshold and high/low increment registers. For the CN10K errata path, only a one-second period is accepted and an hrtimer periodically rewrites the threshold before the hardware rollover boundary. Removal cancels the timer when needed, disables PTP in `PTP_CLOCK_CFG`, and frees the in-memory object.

## State and Persistence Behavior
Persistent state is hardware-resident in PTP CSRs: clock enable/source bits, compensation, timestamp capture, atomic update registers, PPS threshold/increment, and rollover registers. Driver state is runtime-only in `struct ptp`: PCI device, mapped CSR base, selected timestamp reader, spinlock, hrtimer, last hrtimer timestamp, clock rate, and computed clock period. `first_ptp_block` is a single global pointer/error sentinel used by RVU probe. There is no disk persistence, and RVU releases only the PCI device reference through `ptp_put()`.

## Dependencies and Integration Points
The file depends on Linux PCI, MMIO, hrtimer, ktime, bitfield, and module APIs. It integrates with `rvu.c` through `ptp_get()`, `ptp_put()`, `ptp_start()`, and the exported `ptp_driver`. It depends on mailbox definitions from `mbox.h` for request/response layouts and on RVU silicon helpers such as `is_rvu_otx2()` for atomic-update capability checks. Firmware data consumed by `rvu_probe()` supplies SCLK, external clock, and external timestamp selector values.

## Risks and Edge Cases
- `first_ptp_block` represents only the first PTP block; multi-block systems would need careful handling.
- `ptp_atomic_adjtime()` has a suspicious negative large-delta branch that sets `ptp_clock_hi = delta - ptp_clock_hi` when the current counter is smaller than the delta; that may not represent a signed subtract modulo the full timestamp domain.
- `ptp_put()` assumes a non-error pointer; callers must not pass an `ERR_PTR`.
- CN10K A0/A1 PPS support is constrained to one-second periods and depends on hrtimer scheduling close to the rollover boundary.
- `ptp_calc_adjusted_comp()` uses integer arithmetic and a loop around rollover behavior; regression tests should cover low/high clock rates and errata variants.
- `ptp_remove()` frees the object but does not explicitly clear `first_ptp_block`; driver unload ordering currently protects normal use, but stale global pointer behavior would be risky under unusual hot-remove ordering.

## Test Signals
- Build and probe with OcteonTX2 and CN10K device IDs, including CN10K A0/A1 errata revisions and later silicon.
- Exercise mailbox operations for clock read, captured timestamp read, fine adjustment, atomic set, atomic adjust, PPS enable/disable, and threshold set.
- Verify `ptp_get()` returns `-ENODEV` with no hardware, `-EPROBE_DEFER` before PTP probe, and probe errors when `ptp_probe()` fails.
- Inject invalid PPS periods on errata devices and periods above eight seconds on all devices.
- Confirm hrtimer cancellation on PPS disable/remove and absence of timer callbacks after teardown.
- Compare adjusted hardware clock drift against expected scaled ppm for both normal and errata compensation paths.
