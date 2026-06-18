# sources/distributed-fs/ceph-client/kernel/sysctl.c

## Purpose
`sysctl.c` implements generic sysctl proc handlers for strings, signed/unsigned integer vectors, bools, u8 values, unsigned long vectors, large bitmaps, and static keys. It also registers a few base `kernel.*` sysctls and provides `-ENOSYS` stubs when proc sysctl support is disabled.

## Important APIs, types, and functions
- Shared exported constants: `sysctl_vals[]` and `sysctl_long_vals[]`.
- String handler: `_proc_do_string()` and exported `proc_dostring()`.
- Numeric parsing/output helpers: `strtoul_lenient()`, `proc_get_long()`, `proc_put_long()`, `proc_put_char()`, whitespace/skipping helpers.
- Conversion helpers: `proc_uint_u2k_conv_uop()`, `proc_uint_k2u_conv()`, `proc_uint_conv()`, `proc_int_k2u_conv_kop()`, `proc_int_u2k_conv_uop()`, `proc_int_conv()`.
- Proc handlers: `proc_dointvec()`, `proc_douintvec()`, `proc_dointvec_minmax()`, `proc_douintvec_minmax()`, `proc_dou8vec_minmax()`, `proc_doulongvec_minmax()`, `proc_doulongvec_minmax_conv()`, `proc_dointvec_conv()`, `proc_douintvec_conv()`, `proc_do_large_bitmap()`.
- Static-key handler: `proc_do_static_key()`.
- Base table: `sysctl_subsys_table` and `sysctl_init_bases()`.

## Control flow
Read handlers validate table data/maxlen and file position, convert kernel values to ASCII, append delimiters/newlines, update `lenp` and `ppos`, and use `READ_ONCE()` where appropriate. Write handlers enforce strict/warn/legacy write-position policy, cap input parsing to page-sized chunks, parse ASCII numbers, validate sign/range/min/max, write values with `WRITE_ONCE()`, and update file position. Large bitmap writes parse comma/range syntax into a temporary bitmap and copy/or it into the destination depending on position. Static-key writes require `CAP_SYS_ADMIN`, read/update a temporary int through min/max int handling, then enable or disable the static key under a mutex.

## State and persistence behavior
Most handlers mutate external kernel variables referenced by `struct ctl_table::data`; this file supplies parsing and validation but not ownership of those variables. Internal persistent state includes `sysctl_writes_strict` and the base kernel sysctl table. When `CONFIG_PROC_SYSCTL` is absent, exported handlers persist as stubs returning `-ENOSYS`.

## Dependencies and integration points
It integrates with procfs sysctl registration, `struct ctl_table`, capability checks, static keys, bitmap allocation/parsing, `kstrtox` internals, user-copy conventions, and exported symbols consumed by many kernel subsystems registering sysctls. `sys.c` uses `proc_dointvec_minmax()` for overflow UID/GID sysctls.

## Risks
Parsing is ABI-sensitive. Strict file-position behavior affects userspace that writes sysctl values in multiple writes. Numeric overflow, signed negation, truncation at `PAGE_SIZE`, and range checks are common bug surfaces. `proc_do_large_bitmap()` must avoid partial malformed range commits; it uses a temporary bitmap to reduce that risk. External callers must provide correct `maxlen`, data type, and min/max pointer types.

## Test signals
`sysctl-test.c` covers `proc_dointvec()` edge cases. Additional signals are procfs sysctl selftests, LTP sysctl coverage, fuzzing malformed numeric/bitmap input, strict write-position tests, capability tests for `proc_do_static_key()`, and build coverage with `CONFIG_PROC_SYSCTL=n`.
