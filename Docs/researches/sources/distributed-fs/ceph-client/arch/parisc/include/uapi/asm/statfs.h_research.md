<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h

Source read size: 8 lines, 181 bytes.

Purpose: selects the PA-RISC word type for `statfs` structures and includes the generic layout. Important API: `__statfs_word` is `long`. Control flow: statfs/fstatfs syscalls use the resulting generic structure layout. State and persistence: filesystem statistics are returned as snapshots. Dependencies and integration points: generic statfs UAPI and VFS statfs implementations. Risks: word-size differences affect 32/64-bit userspace structure layout. Test signals: statfs/fstatfs tests on several filesystem types and compat layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/statfs.h -->
