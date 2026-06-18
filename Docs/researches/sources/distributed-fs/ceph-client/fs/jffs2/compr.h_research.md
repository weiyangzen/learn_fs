# sources/distributed-fs/ceph-client/fs/jffs2/compr.h

## Purpose
`compr.h` defines the compressor abstraction and compression policy constants shared by the JFFS2 compression manager and backend implementations. It is the contract that lets the filesystem register optional algorithms while keeping write, read, and GC code independent of individual compressor internals.

## Important APIs, Types, And Functions
`struct jffs2_compressor` contains list linkage, priority, human name, on-flash compression id, `compress`/`decompress` callbacks, disable/use counters, scratch buffer fields used by size-selection mode, and statistics counters. The header defines backend priorities, default-disabled Rubin flags, compression policy constants (`NONE`, `PRIORITY`, `SIZE`, `FAVOURLZO`, `FORCELZO`, `FORCEZLIB`), and `FAVOUR_LZO_PERCENT`. It declares the registry API and the module init/exit hooks for zlib, rtime, Rubin, and LZO, with inline no-op stubs when a backend is not configured.

## Control Flow
Consumers call `jffs2_compress()` and `jffs2_decompress()` rather than backend functions directly. During filesystem module initialization, `jffs2_compressors_init()` calls the backend init functions exposed here; during teardown, `jffs2_compressors_exit()` calls the corresponding exits.

## State And Persistence Behavior
The header does not persist data itself, but it defines the compression id and policy machinery that affects `jffs2_raw_inode.compr` and `usercompr` fields on flash. The scratch buffer and stats fields are in-core backend state, while `usecount` and `disabled` influence runtime availability.

## Dependencies And Integration Points
It includes kernel allocation/list/types headers, JFFS2 VFS inode and superblock headers, and `nodelist.h`. Backends include this header to publish a static `struct jffs2_compressor`; write/read/GC paths include it to call compression APIs.

## Risks And Test Signals
The major compatibility risk is that the `compr` byte in each backend must match `linux/jffs2.h` on-flash constants forever. Priority values also affect default behavior. Tests should verify configured-out backends compile through stubs, all configured backends register/unregister cleanly, and old images using disabled/decompress-only algorithms still read.
