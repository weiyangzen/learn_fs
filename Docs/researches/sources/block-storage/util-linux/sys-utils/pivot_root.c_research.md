# File Research: sources/block-storage/util-linux/sys-utils/pivot_root.c

This small file implements `pivot_root(8)` as a direct wrapper around the `SYS_pivot_root` syscall. It accepts only `new_root` and `put_old` positional arguments plus help/version options.

The command performs locale/stdout setup, validates exactly two arguments, calls `pivot_root(argv[1], argv[2])`, and reports a fatal error if the syscall fails. It intentionally leaves all mount namespace setup and path preparation to the caller.
