# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_cmn_err.c

FreeBSD implementation of Solaris-style `cmn_err()` logging.

Key behavior:
- `vcmn_err()` maps severities to prefixes: continuation, notice, warning, panic, or ignore.
- Panic severity formats into a local buffer and calls FreeBSD `panic()`.
- Non-panic severities print through `printf()`/`vprintf()` with a newline.
- `cmn_err()` is the variadic wrapper.

Unknown severity levels panic.
