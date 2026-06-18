# sources/distributed-fs/ceph-client/arch/microblaze/kernel/sys_microblaze.c

Purpose: implements MicroBlaze-specific mmap syscall wrappers.

Important APIs and state: `SYSCALL_DEFINE6(mmap, ...)` and `SYSCALL_DEFINE6(mmap2, ...)` validate offset alignment and call `ksys_mmap_pgoff()`.

Control flow: `mmap` expects byte offset in `pgoff` and rejects offsets not page aligned, then shifts by `PAGE_SHIFT`. `mmap2` expects 4 KiB units and rejects bits outside the page-granular range before shifting by `PAGE_SHIFT - 12`.

State and persistence: no architecture state; successful calls create VMAs through common mm code.

Dependencies and integration: entries are referenced by generated syscall table and invoked by `entry.S` syscall dispatch.

Risks and test signals: offset validation must match userspace ABI. Test mmap/mmap2 with aligned and misaligned offsets, large files, and 4 KiB page assumptions.
