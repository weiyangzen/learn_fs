# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_dtrace.c

Minimal FreeBSD SDT/DTrace probe definition file.

It defines one probe:
- `SDT_PROBE_DEFINE1(sdt, , , set__error, "int")`

This supports the SPL/ZFS `set_error` tracing point on FreeBSD.
