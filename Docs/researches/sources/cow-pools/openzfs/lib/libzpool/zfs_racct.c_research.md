# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_racct.c

Libzpool stubs for FreeBSD resource-accounting hooks.

Functions:
- `zfs_racct_read()`
- `zfs_racct_write()`

Both accept SPA, size, IOPS, and DMU flags but intentionally do nothing in the libzpool/userland environment.
