# sources/distributed-fs/ceph-client/fs/pstore/platform.c

## Purpose
`platform.c` is the generic pstore core. It registers one backend, captures kmsg dumps, optional console/ftrace/pmsg streams, compresses dmesg records, and populates the pstore filesystem from backend records.

## Important APIs, types, and functions
Exported APIs include `pstore_register`, `pstore_unregister`, `pstore_type_to_name`, `pstore_name_to_type`, `pstore_record_init`, `pstore_get_backend_records`, and `pstore_set_kmsg_bytes`. Key helpers are `pstore_dump`, compression allocation/free, `decompress_record`, console write hook, `pstore_write_user_compat`, and timer/workqueue update functions.

## Control flow
Backend registration validates flags and read/write callbacks, installs default `write_user` if needed, initializes backend locks, allocates compression buffers for dmesg, scans existing records, and registers enabled frontends. Kmsg dumping snapshots up to `kmsg_bytes`, optionally deflates data, writes one or more records, and schedules delayed filesystem refresh for oops records. Backend reads loop up to 65,536 records, decompress supported dmesg entries, and pass them to `pstore_mkfile`.

## State and persistence
Only one backend is active in global `psinfo`. Persistent state is backend-owned; core state includes compression buffers, oops counters, refresh timer/work item, selected backend parameter, and filesystem record buffers.

## Dependencies and integration points
It integrates kmsg dumpers, consoles, pstorefs, zlib, timers/workqueues, module parameters, optional frontends, and backend callback contracts.

## Risks and test signals
Risks include blocking in panic/NMI paths, compression workspace allocation failure, backend read loops, single-backend conflicts, decompression trust in record metadata, and unregister races with timer/work. Test signals include panic and oops capture, compression fallback, backend selection parameter, console/pmsg/ftrace registration, delayed oops refresh, and corrupt compressed record handling.
