# sources/distributed-fs/ceph-client/kernel/time/namespace_internal.h

Purpose: private bridge between time namespace core and VDSO implementation. It declares `timens_offset_lock` and the VVAR page allocation/free hooks used by namespace cloning and teardown.

Important APIs and types: forward-declares `struct time_namespace`; exports `timens_offset_lock` for offset/VDSO freeze serialization; declares `timens_vdso_alloc_vvar_page()` and `timens_vdso_free_vvar_page()` when `CONFIG_TIME_NS_VDSO` is enabled. When VDSO support is disabled, inline stubs make allocation a no-op success and freeing a no-op.

State and persistence: this header owns no storage beyond the external mutex declaration. Its conditional stubs define whether a time namespace has per-namespace VVAR page lifecycle behavior.

Dependencies and integration: included by `namespace.c` and `namespace_vdso.c`; depends only on mutex definitions and time namespace type visibility. It separates generic namespace lifetime logic from architecture/config-dependent VDSO mapping support.

Risks and test signals: risks are mostly configuration skew: namespace clone/free must behave identically when VDSO support is compiled out. Build-test both `CONFIG_TIME_NS_VDSO=y` and `n`, verify no duplicate definitions, and exercise clone failure unwinding when VVAR allocation fails.
