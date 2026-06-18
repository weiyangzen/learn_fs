# sources/distributed-fs/ceph-client/tools/debugging/kernel-chktaint

Purpose: Decodes the Linux kernel taint bitmask from `/proc/sys/kernel/tainted` or a supplied integer, printing reasons, the taint string, and tainted modules.

Important APIs, types, and functions: Shell `usage()` prints help. `addout()` appends one-character taint flags to `out`. The main body shifts through taint bits 0 through 19 and prints descriptions for set bits.

Control flow: Validates optional integer/help argument, reads `/proc/sys/kernel/tainted` when no argument, exits early for zero, repeatedly tests `T % 2`, appends the corresponding flag or space, divides `T` by 2, prints raw value/string, optionally scans `/sys/module/*/taint`, and prints documentation pointers.

State and persistence: Read-only. No persistent state.

Dependencies and integration points: Uses `/proc/sys/kernel/tainted`, `/sys/module`, and standard shell utilities. Aligns with Linux tainted-kernels documentation.

Risks: Script declares `/bin/sh` but uses `==`, which is not POSIX in all shells. Numeric tests and unquoted variables are mostly controlled but still shell-sensitive. Bit descriptions must track kernel taint flag additions.

Test signals: Run with `0`, known integer masks, invalid input, no argument on a live kernel, and under different `/bin/sh` implementations.
