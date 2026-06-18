# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ptp.c

## Purpose
`ptp.c` implements e1000e PTP Hardware Clock support for devices with hardware timestamp capability. It adapts e1000e SYSTIM/TIMINCA registers to the Linux PHC API through `ptp_clock_info`, `cyclecounter`, and `timecounter` operations.

## Important APIs, types, and functions
The PHC callbacks are `e1000e_phc_adjfine`, `e1000e_phc_adjtime`, `e1000e_phc_gettimex`, `e1000e_phc_settime`, and `e1000e_phc_enable`. When `CONFIG_E1000E_HWTS` is enabled, `e1000e_phc_getcrosststamp` and `e1000e_phc_get_syncdevicetime` provide ART/device cross timestamps. Lifecycle functions are `e1000e_ptp_init` and `e1000e_ptp_remove`; overflow maintenance is handled by delayed work `e1000e_systim_overflow_work`.

## Control flow
Initialization exits early unless `FLAG_HAS_HW_TIMESTAMP` is set. It copies the static `ptp_clock_info`, names the clock from the permanent MAC address, selects `max_adj` from `hw->mac.type` and the `TSYNCRXCTL` clock-source bit, optionally enables cross timestamp support on ART-capable systems, initializes delayed overflow work, schedules it, and registers the PHC. PHC operations take `adapter->systim_lock`, read or adjust the timecounter, and write TIMINCA when frequency changes.

## State and persistence behavior
Persistent driver state includes `adapter->ptp_clock`, `ptp_clock_info`, `ptp_delta`, `tc`, `cc`, and the delayed work item. Hardware state is in TIMINCA, SYSTIM, RX/TX timestamp registers, and cross timestamp latches. `adjfine` changes the hardware increment value and records the requested delta; `settime` reinitializes the software timecounter base without directly rewriting all hardware time registers.

## Dependencies and integration points
The file depends on the Linux PTP clock framework, timecounter/cyclecounter helpers, spinlocks, delayed work, and e1000e helpers such as `e1000e_get_base_timinca` and `e1000e_read_systim`. It integrates with probe/remove, timestamp ioctl paths, ethtool timestamp reporting elsewhere, and optional x86 ART cross timestamp support.

## Risks
The code explicitly notes non-monotonic SYSTIM readings, so lock coverage and timecounter conversion are critical. Wrong `max_adj` selection can allow invalid frequency adjustments for a clock source. Cross timestamp support has a short polling timeout and hardware latch dependency. Registering delayed work before PHC registration means remove paths must always cancel work for timestamp-capable devices.

## Test signals
Signals include PHC registration/removal logs, `ptp4l`/`phc2sys` frequency and time adjustment behavior, stable `gettimex64` readings, successful cross timestamp calls on ART-capable systems, overflow work rescheduling, and clean driver unload without delayed work or PHC leaks.
