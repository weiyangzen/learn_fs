# sources/distributed-fs/openafs/src/afs/afs_osidnlc.h

## Purpose
`afs_osidnlc.h` defines the data structures and constants for the OSI directory name lookup cache implemented by `afs_osidnlc.c`.

## Important APIs, types, and functions
The header defines `AFSNCNAMESIZE` as 36 bytes, `struct nc`, and `dnlcstats_t`. `struct nc` contains a hash key, next/previous circular-list pointers, directory and target vcache pointers, and the cached name bytes. `dnlcstats_t` contains counters for enters, lookups, misses, removes, directory purges, vnode purges, volume purges, full purges, cycles, and lookup races.

## Control flow
There is no executable control flow in this header, but the fixed name size and structure layout directly shape DNLC behavior: only names shorter than `AFSNCNAMESIZE` are cached, hash membership is tracked with `prev != NULL`, and entries can be moved between circular hash buckets and the freelist.

## State and persistence behavior
The structures define volatile in-memory cache entries and counters. No data is persisted.

## Dependencies and integration points
The header assumes `struct vcache` is visible or forward-declared by including sources. It is included by DNLC implementation and several PAG/NFS-related sources that need DNLC declarations indirectly through broader AFS includes.

## Risks and edge cases
The name array comment notes possible null-byte waste; actual implementation copies names including the terminator and rejects names that would not fit. Changing `AFSNCNAMESIZE` affects memory footprint and lookup cache hit rate. Structure layout changes affect fixed `nameCache` memory use.

## Test signals
Validate build compatibility for all includers, DNLC name-size boundary behavior, stats counter reads, and no accidental ABI assumptions in debugging tools.
