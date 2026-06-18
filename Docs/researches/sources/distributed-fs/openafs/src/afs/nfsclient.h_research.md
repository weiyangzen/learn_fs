# sources/distributed-fs/openafs/src/afs/nfsclient.h

Purpose: defines per-NFS-client PAG/exporter state for the NFS/AFS translator.

Important APIs/types: constants `NNFSCLIENTS`, `NHash(host)`, `NFSCLIENTGC`, and `NFSXLATOR_CRED`. `struct nfsclientpag` overlays its first fields with `struct afs_exporter`, then adds refcount, UID, host, PAG, client UID, per-client `@sys` values, count, and `lastcall`.

Control flow: no functions; hash and timeout constants guide implementation elsewhere. Entries are looked up by host/UID and garbage-collected after `NFSCLIENTGC`.

State and persistence: in-memory translator state only. PAG and sysname values preserve remote client identity between calls.

Dependencies and integration points: depends on `exporter.h` layout and `MAXNUMSYSNAMES` from AFS headers. Used by NFS translator request handling and by vcache partial-FID lookup paths.

Risks: overlay layout with `afs_exporter` must remain stable. Host hash is simple bitmasking and assumes table size is a power of two. Stale PAG/sysname state can leak remote identity behavior until GC.

Test signals: hash distribution, GC after 24 hours, refcount balance, sysname propagation, host/UID distinction, and translator credential detection via `NFSXLATOR_CRED`.
