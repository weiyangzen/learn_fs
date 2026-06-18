# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sunddi.c

Small subset of Solaris DDI string conversion helpers for FreeBSD.

Functions:
- `ddi_strtol()`
- `ddi_strtoull()`
- `ddi_strtoll()`

Each calls the corresponding FreeBSD/libkern conversion routine and returns 0 without detailed errno translation.
