# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spufs.h

Purpose: central private interface for spufs. It declares context/gang data structures, filesystem descriptor types, operation tables, syscall hooks, coredump hooks, and cross-file helpers.

Important types: `struct spu_context` combines hardware binding, CSA, mappings, owner mm, refs, wait queues, scheduler fields, statistics, switch log, and affinity links. `struct spu_gang` holds grouped contexts and affinity metadata. `struct spu_context_ops` abstracts live hardware vs saved backing operations. Other key structs are `mfc_dma_command`, `spufs_inode_info`, `spufs_tree_descr`, and `spufs_coredump_reader`.

Integration points: `spu_hw_ops` and `spu_backing_ops` implement the operations ABI; `spufs_dir_contents` and related arrays define VFS contents; `spufs_calls` registers create/run callbacks with architecture syscall glue. The header declares scheduler, context, fault, switch, coredump, gang, and allocation functions used across files.

State and dependencies: includes Linux VFS/refcount/lock headers and PowerPC SPU CSA/info headers. Risks include ABI-wide changes to `spu_context_ops`, lock ownership assumptions not encoded in types, and structure layout dependencies shared with coredump/debug users. Test signals are full `CONFIG_SPU_FS` build, sparse/lockdep coverage, and successful switching between `spu_backing_ops` and `spu_hw_ops`.
