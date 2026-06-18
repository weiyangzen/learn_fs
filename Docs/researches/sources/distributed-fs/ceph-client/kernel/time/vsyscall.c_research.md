# sources/distributed-fs/ceph-client/kernel/time/vsyscall.c

## Purpose

`vsyscall.c` is the generic kernel-side updater for VDSO/vsyscall time data. It copies timekeeper state into `vdso_k_time_data` so user space can read common clocks without a syscall, while preserving seqlock-style consistency and architecture-specific synchronization.

## Important APIs, types, and functions

- `fill_clock_configuration()` copies clocksource read-base parameters into a `vdso_clock`: cycle base, optional overflow limit, mask, multiplier, and shift.
- `update_vdso_time_data()` updates high-resolution VDSO base times for `CLOCK_MONOTONIC`, `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC_RAW`, and `CLOCK_TAI`.
- `update_vsyscall()` is the main timekeeper update hook. It updates realtime, coarse realtime, coarse monotonic, hrtimer resolution, high-resolution clocks if VDSO-capable, and architecture clock metadata.
- `update_vsyscall_tz()` copies `sys_tz` timezone fields into VDSO data.
- Under `CONFIG_POSIX_AUX_CLOCKS`, `vdso_time_update_aux()` updates an auxiliary timekeeper's VDSO clock slot.
- `vdso_update_begin()` and `vdso_update_end()` let architecture code update arch-specific VDSO data while holding the timekeeper lock and invalidating/restoring the VDSO sequence counter.

## Control flow

`update_vsyscall()` starts with `vdso_write_begin(vdata)`, writes the active VDSO clock mode into the high-resolution/coarse and raw clock slots, updates realtime and coarse basetimes, stores `hrtimer_resolution`, and then only refreshes high-resolution derived clocks if `clock_mode != VDSO_CLOCKMODE_NONE`. It calls `__arch_update_vdso_clock()` for both generic clock slots, ends the sequence with `vdso_write_end()`, and finally calls `__arch_sync_vdso_time_data()`.

`update_vdso_time_data()` performs shifted-nanosecond arithmetic using `tk->tkr_mono.shift`. It normalizes monotonic and boottime nanoseconds by subtracting one shifted second until the value is below a second, copies raw time directly from `tkr_raw`, and computes TAI by adding `tai_offset` to realtime seconds.

`vdso_time_update_aux()` selects the auxiliary clock slot by `tk->id - TIMEKEEPER_AUX_FIRST`, disables VDSO use when `tk->clock_valid` is false, and otherwise fills clock configuration and computes the auxiliary basetime from `monotonic_to_aux`.

`vdso_update_begin()` acquires the timekeeper lock with IRQ save and marks VDSO data inconsistent. `vdso_update_end()` reverses this by marking data consistent, syncing to architecture storage, and releasing the lock/IRQs.

## State and persistence behavior

The persistent target is the global VDSO time data page referenced by `vdso_k_time_data`. Updates are protected by VDSO sequence helpers so concurrent user readers can detect in-progress writes. `hrtimer_res`, timezone fields, clock modes, clocksource conversion parameters, and basetime arrays persist until the next timekeeper update. No dynamic memory is allocated.

## Dependencies and integration points

The file depends on `linux/timekeeper_internal.h`, VDSO datapage/helper APIs, hrtimer resolution, `sys_tz`, architecture hooks (`__arch_update_vdso_clock()` and `__arch_sync_vdso_time_data()`), and internal timekeeping lock helpers from `timekeeping_internal.h`. It is called from core timekeeping update paths and may be used by architecture code for additional VDSO fields.

## Risks and edge cases

- Shifted nanosecond arithmetic must stay normalized; incorrect carry handling would return invalid monotonic or boottime basetimes to user space.
- VDSO writes must be bracketed by sequence updates. Missing `vdso_write_end()` or architecture sync can expose inconsistent or stale data.
- If a clocksource is not VDSO capable, high-resolution fields are intentionally skipped; consumers must fall back to syscalls when `VDSO_CLOCKMODE_NONE` is published.
- Auxiliary clock indexing depends on valid `timekeeper` IDs and `clock_valid`; a bad ID would select the wrong slot.
- `update_vsyscall_tz()` writes timezone values without the main timekeeper sequence wrapper; correctness depends on the architecture/VDSO synchronization contract for these fields.

## Test signals

Test signals include VDSO clock_gettime comparisons against syscall results for realtime, monotonic, boottime, raw, TAI, coarse clocks, timezone update tests, clocksource changes to/from non-VDSO mode, and architecture-specific VDSO synchronization tests. Timekeeping selftests should watch for monotonic regressions, incorrect coarse normalization, and invalid hrtimer resolution exposure.
