# File Research: sources/cow-pools/openzfs/lib/libzpool/include/Makefile.am

Installs libzpool-specific public compatibility headers under `$(includedir)/libzpool/sys`.

Headers exported:
- `abd_os.h`
- `abd_impl_os.h`
- `trace_zfs.h`
- `zfs_bootenv_os.h`
- `zfs_context_os.h`
- `zfs_debug_os.h`

This file only defines installation paths and header list; it has no build logic beyond header distribution.
