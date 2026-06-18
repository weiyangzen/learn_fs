# sources/distributed-fs/ceph-client/fs/pstore/zone.c

## Purpose
`zone.c` is an intermediate pstore backend that divides one contiguous storage device into in-memory zones for kmsg, pmsg, console, and ftrace, then flushes those zones to block-like storage.

## Important APIs, types, and functions
Public APIs are `register_pstore_zone` and `unregister_pstore_zone`. Core structures are `psz_buffer`, `psz_kmsg_header`, `pstore_zone`, and `psz_context`. Important helpers cover zone allocation, recovery, dirty flushing, circular writes, kmsg header read/write, record erase, pstore read/write callbacks, and delayed cleaner work.

## Control flow
Registration validates size/alignment and read/write callbacks, allocates zones in pmsg, console, ftrace, and dmesg order, allocates a dmesg pstore buffer, sets frontend flags, and registers with pstore. Reads lazily recover storage into memory, choosing active kmsg write position from timestamps and preserving old pmsg/console/ftrace buffers. Writes update in-memory circular buffers and attempt immediate flush; panic kmsg writes use `panic_write` if available and then flush dirty zones.

## State and persistence
Persistent state lives in backend storage as per-zone `psz_buffer` headers and data. Runtime state tracks write/read counters, recovered/on-panic atomics, dirty flags, and old buffers for recovered records.

## Dependencies and integration points
It integrates pstore core, pstore/blk or other `pstore_zone_info` providers, delayed work, block-sector alignment, kmsg dump reasons, and pstore ftrace log merging.

## Risks and test signals
Risks include dirty data not flushed before unregister, recovery trusting corrupted metadata, panic-path writes without `panic_write`, broken-zone retry behavior, ftrace per-CPU size division, erase semantics with new data present, and single backend ownership. Test signals include corrupted signatures/datalen, backend `-ENOMSG` injection, panic writes, delayed flush retry, unlink erase, ftrace merge, and all size alignment checks.
