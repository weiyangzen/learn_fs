## sources/distributed-fs/ceph-client/lib/raid6/unroll.awk

Purpose: small source-generation filter used by RAID-6 tests and template-based SIMD/integer implementations to expand unrolled code templates.

Important behavior: it requires `-vN=n`, converts `N` to numeric `n`, and for each input line repeats lines containing `$$` exactly `n` times. In each repeated line it replaces `$$` with the current repeat index, `$#` with the unroll count, and `$*` with a literal dollar sign.

Control flow: the script initializes `n` in `BEGIN`, sets `rep` per line based on whether `$$` is present, loops `i` from 0 to `rep-1`, applies `gsub()` transformations, and prints the resulting line.

State and persistence: no persistent state beyond current input line and loop counters. Output is generated source on stdout.

Dependencies/integration: called from `raid6/test/Makefile` to expand `int.uc`, `neon.uc`, `altivec.uc`, and `vpermxor.uc` into unroll-specific `.c` files.

Risks/test signals: the filter is intentionally simple; malformed templates or missing `-vN` silently produce wrong or empty-style expansion. Build success and later RAID-6 test correctness are the practical signals that generated code is coherent.
