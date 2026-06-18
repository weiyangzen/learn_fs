# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/valid-adjtimex.c

## Purpose
This test validates valid, out-of-range, and invalid `adjtimex()` frequency inputs plus valid and invalid `ADJ_SETOFFSET` values for microsecond and nanosecond modes.

## Important APIs, Types, and Functions
`clock_adjtime()` wraps the raw syscall. `clear_time_state()` clears NTP status. `validate_freq()` applies arrays of valid, out-of-range, and invalid `tx.freq` values. `set_offset()`, `set_bad_offset()`, and `validate_set_offset()` exercise `ADJ_SETOFFSET` with and without `ADJ_NANO`.

## Control Flow
`main()` runs frequency validation first, then set-offset validation. Frequency tests expect valid values to set, out-of-range values to be clamped or rejected without storing the exact value, and 64-bit `LONG_MAX/MIN` values to fail. Offset tests apply normalized positive and negative offsets and reject malformed subsecond fields.

## State and Persistence
The test modifies kernel frequency and realtime offset. It resets frequency to zero after `validate_freq()`, but it does not otherwise restore external time synchronization state.

## Dependencies and Integration Points
It depends on `adjtimex`, raw `clock_adjtime`, VDSO time constants, and privileges for time adjustment. It uses kselftest exit helpers.

## Risks
The test can perturb system clock discipline and should not run with active time synchronization unless isolated. It defines `ADJ_SETOFFSET` locally, so it assumes the UAPI value is stable. The checks are sensitive to how kernels clamp out-of-range frequency values.

## Test Signals
Pass means accepted frequency values persist as requested, disallowed values are not accepted as exact active frequency, invalid 64-bit sentinels fail, normalized offsets apply, and malformed subsecond offsets are rejected.
