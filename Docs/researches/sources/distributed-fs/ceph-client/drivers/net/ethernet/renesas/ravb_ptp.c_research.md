# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb_ptp.c

## Purpose
This file implements the PTP Hardware Clock support for the Renesas Ethernet AVB driver. It registers the AVB gPTP clock, adjusts frequency and time, reads/writes the hardware timer, supports one external timestamp input, supports one periodic output, and services gPTP interrupt events for external timestamp and compare-match periodic output.

## Important APIs, Types, And Functions
- Clock operations: `ravb_ptp_info` provides `adjfine`, `adjtime`, `gettime64`, `settime64`, and `enable` callbacks to the PTP core.
- Timer register helpers: `ravb_ptp_tcr_request()`, `ravb_ptp_time_read()`, `ravb_ptp_time_write()`, and `ravb_ptp_update_compare()` serialize GCCR requests and access `GCT*`, `GTO*`, `GTI`, and `GPTC`.
- Feature controls: `ravb_ptp_extts()` toggles external timestamp interrupt masks, and `ravb_ptp_perout()` configures compare target/period and enables or disables compare interrupts.
- Driver integration: `ravb_ptp_interrupt()`, `ravb_ptp_init()`, and `ravb_ptp_stop()` are called by `ravb_main.c`.

## Control Flow
Initialization copies `ravb_ptp_info` into `priv->ptp.info`, records the default/current addend from `GTI`, waits for no outstanding timer request, selects adjusted gPTP time in `GCCR_TCSS`, and registers a PTP clock. Frequency adjustment computes a new addend with `adjust_by_scaled_ppm()`, updates `priv->ptp.current_addend`, writes `GTI`, and requests hardware load through `GCCR_LTI`. Time adjustment reads the current time under `priv->lock`, converts to nanoseconds, adds the delta, and writes the new time through the timer reset/load sequence.

External timestamp enablement accepts only index 0 and toggles either legacy `GIC_PTCE` or separate enable/disable registers (`GIE_PTCS`/`GID_PTCD`) depending on hardware. Periodic output accepts only index 0, validates that start and period fit in 32-bit nanosecond compare registers, writes the next compare value, stores target/period in `priv->ptp.perout[0]`, and enables compare interrupts. The interrupt handler reads enabled `GIS` bits, emits `PTP_CLOCK_EXTTS` events with `GCPT`, advances periodic targets by period on compare matches, rewrites `GPTC`, and clears handled status bits.

## State And Persistence
PTP state is stored inside `struct ravb_private` as `priv->ptp.clock`, copied `ptp_clock_info`, `default_addend`, `current_addend`, one `extts[]` enable flag, and one `perout[]` target/period. Hardware timer state resides in AVB gPTP registers and survives only until hardware reset or reinitialization. There is no disk persistence.

## Dependencies And Integration Points
The file depends on `ravb.h`, Linux PTP clock APIs, `timespec64`/ktime helpers, spin locking supplied by `priv->lock`, and `ravb_read()`/`ravb_write()`/`ravb_modify()`/`ravb_wait()` from `ravb_main.c`. It is linked into the composite `ravb.o` object and is initialized/stopped by open/close, ring resize, timeout recovery, suspend/WoL, and resume paths in `ravb_main.c`.

## Risks And Edge Cases
- All multi-register timer reads/writes require `priv->lock`; callers and interrupt paths must preserve that contract.
- `ravb_ptp_update_compare()` clamps compare values away from timer increment wrap hazards, but `perout->target += period` can still wrap naturally in 32 bits.
- `ravb_ptp_init()` does not check `ptp_clock_register()` for errors before later users call `ptp_clock_index()` in `ravb_main.c`; failures could propagate as invalid PHC state.
- `ravb_ptp_stop()` unconditionally unregisters `priv->ptp.clock`; repeated stop or failed init paths need matching lifecycle.
- Hardware paths differ for `irq_en_dis`, so Gen2-style mask writes and Gen3+ enable/disable registers need separate testing.

## Test Signals
Check `ethtool -T` PHC index, `phc2sys`/`testptp` get/set/adjfine/adjtime behavior, external timestamp event delivery, periodic output programming and repeated compare interrupts, interrupt-mask behavior on both old and `irq_en_dis` hardware, PTP lifecycle across open/close/ring resize/suspend/resume, and error handling when timer request bits remain busy.
