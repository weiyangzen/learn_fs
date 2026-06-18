# sources/distributed-fs/ceph-client/fs/pstore/pmsg.c

## Purpose
`pmsg.c` exposes `/dev/pmsg0`, a write-only user-space channel that stores messages in the active pstore backend as `PSTORE_TYPE_PMSG`.

## Important APIs, types, and functions
Important functions are `write_pmsg`, `pstore_register_pmsg`, `pstore_unregister_pmsg`, and `pmsg_devnode`. State includes `pmsg_lock`, `pmsg_class`, and dynamically allocated `pmsg_major`.

## Control flow
Registration allocates a char-device major, creates a class with mode `0220`, and creates `pmsg0`. Writes validate nonzero count and `access_ok`, initialize a pstore record, serialize with `pmsg_lock`, and call `psinfo->write_user`.

## State and persistence
The char device has no persistent state. Message bytes persist only if the backend implements and stores `PSTORE_TYPE_PMSG`.

## Dependencies and integration points
It integrates char devices, class/device creation, uaccess checks, pstore platform registration, and backend `write_user`.

## Risks and test signals
Risks include missing backend `write_user`, unregister after partial registration, large user writes, and concurrent writers. Test signals include device node mode, write with invalid user pointer, backend failure propagation, unregister cleanup, and reboot recovery of pmsg records.
