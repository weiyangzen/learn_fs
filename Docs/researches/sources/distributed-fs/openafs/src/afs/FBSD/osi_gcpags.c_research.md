# sources/distributed-fs/openafs/src/afs/FBSD/osi_gcpags.c

## Purpose
Implements FreeBSD process traversal and credential snapshotting for OpenAFS PAG garbage collection.

## Important APIs, Types, And Functions
`afs_osi_TraverseProcTable` walks `allproc` and calls `afs_GCPAGs_perproc_func`. `afs_osi_proc2cred` copies uid and groups from a live process credential into a static `afs_ucred_t`.

## Control Flow
Traversal skips embryonic, zombie, and system processes. Credential conversion accepts sleeping, running, and stopped processes, locks credentials for reading, copies uid/group fields, unlocks, and returns the static copy.

## State And Persistence
No durable state is stored. The static credential copy is overwritten on each call.

## Dependencies And Integration Points
Depends on FreeBSD process lists, `pcred_readlock`, OpenAFS group/PAG encoding, and the PAG GC scanner.

## Risks
Static returned credentials are not reentrant. Process state can change while scanning. The implementation copies only uid/groups, so callers needing richer credential fields cannot rely on it.

## Test Signals
Token/PAG GC with many process states, concurrent process exit, and repeated credential scans should reclaim stale PAGs without crashes or corrupted group lists.
