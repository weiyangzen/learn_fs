# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/coredump.c

Purpose: contributes Cell/SPU-specific ELF notes to process core dumps. It discovers open spufs context directories and emits one note per reader in `spufs_coredump_read`.

Important APIs: `spufs_coredump_extra_notes_size()` computes extra note bytes; `spufs_coredump_extra_notes_write()` writes the notes; `coredump_next_context()` iterates file descriptors; `spufs_arch_write_note()` emits `NT_SPU` note headers and data.

Control flow: `iterate_fd()` finds files whose operations are `spufs_context_fops`; NOSCHED contexts are skipped. Each context is refcounted, acquired in saved state with `spu_acquire_saved()`, sized or dumped, then released. Dump entries either call a binary dump callback or format a getter value as a fixed hexadecimal string.

State and dependencies: depends on `file.c` for `spufs_coredump_read` and on context locking to produce stable saved data. It assumes coredump-time descriptor tables are not shared in a way that invalidates file references. Risks include note-size/write mismatch, early returns leaking context references in error paths, and dump callbacks returning fewer bytes than declared. Test signals are core dumps from processes holding scheduled spufs contexts, verifying `SPU/<fd>/<name>` notes and alignment.
