# sources/distributed-fs/ceph-client/include/linux/kstrtox.h

## Purpose

`kstrtox.h` declares safe string-to-number conversion helpers for kernel strings and userspace buffers, plus legacy `simple_strto*` functions that should be avoided when strict parsing/range checking is needed. The source was read as a complete 151-line file.

## Important APIs, Types, and Functions

Primary APIs include `_kstrtoul()`, `_kstrtol()`, `kstrtoull()`, `kstrtoll()`, `kstrtoul()`, `kstrtol()`, `kstrtouint()`, `kstrtoint()`, typed wrappers for u64/s64/u32/s32/u16/s16/u8/s8, `kstrtobool()`, and corresponding `_from_user()` helpers. Legacy APIs are `simple_strtoul()`, `simple_strntoul()`, `simple_strtol()`, `simple_strtoull()`, and `simple_strtoll()`.

## Control Flow

Callers pass a NUL-terminated kernel string or counted userspace buffer and base. Base zero auto-detects decimal/octal/hex. Inline long wrappers dispatch to long-long implementations when sizes/alignments match, otherwise use internal long-specific helpers.

## State and Persistence Behavior

No state is stored. Successful conversions write to caller-provided result storage and return zero; errors report parse failure or range overflow.

## Dependencies and Integration Points

It depends on compiler attributes, fixed-width types, and uaccess in implementations. It is widely used by sysfs/procfs/module parameter parsing and kernel text configuration.

## Risks and Edge Cases

Return codes are must-check. Accepted syntax allows a single trailing newline. Base is limited to 16. Legacy simple converters do not check overflow and stop at the first non-digit, so they can silently accept malformed input.

## Test Signals

Conversion unit tests for each width/sign, overflow/underflow tests, invalid character tests, newline handling, base autodetection, `_from_user()` fault tests, and must-check warning coverage are useful.
