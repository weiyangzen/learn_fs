## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.c

Purpose: translates 32-bit and special x32 ioctl ABIs into native XFS operations so compat userspace can use legacy XFS ioctls safely on 64-bit kernels.

Important APIs and functions: `xfs_file_compat_ioctl` is the compat entry point. Alignment-specific helpers under `BROKEN_X86_ALIGNMENT` translate v1 geometry and growfs structs. `xfs_ioctl32_bstime_copyin`, `xfs_ioctl32_bstat_copyin`, `xfs_bstime_store_compat`, and `xfs_fsbulkstat_one_fmt_compat` convert time and bstat layouts. `xfs_compat_ioc_fsbulkstat` handles legacy 32-bit bulkstat/inumbers requests. `xfs_compat_handlereq_copyin`, `xfs_compat_attrlist_by_handle`, and `xfs_compat_attrmulti_by_handle` translate handle and attr-by-handle requests.

Control flow: compat dispatch handles known layout-changing ioctls explicitly, performs pointer conversion with `compat_ptr`, copies compact structs field by field, brackets mutating growfs and swapext paths with `mnt_want_write_file`, and delegates unchanged commands to native `xfs_file_ioctl`. For x32, bulk request pointers are compat-width while output records may use native layout, so the formatter selection is adjusted dynamically.

State and persistence: this file does not implement independent persistent operations; it delegates to native growfs, swapext, handle, attr, bulkstat, and ioctl functions after ABI translation. Persistent effects are therefore the same as native operations.

Dependencies and integration: depends on native ioctl helpers, itable formatters, fsops, attrs, handles, compat user accessors, and architecture layout macros. It must match the compat structs and ioctl numbers in `xfs_ioctl32.h`.

Risks and test signals: field-by-field translations are ABI-sensitive. The `xfs_ioctl32_bstat_copyin` path is especially risky because incorrect source fields corrupt swapext validation. Tests should exercise 32-bit bulkstat, fsinumbers, swapext, handle ioctls, attrlist/attrmulti by handle, x86 packed geometry/growfs, x32 formatter selection, invalid user pointers, overflowed attr op counts, and fallback to native ioctl for unchanged commands.
