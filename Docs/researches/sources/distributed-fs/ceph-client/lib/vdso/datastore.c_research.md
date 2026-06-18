<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/datastore.c -->
# sources/distributed-fs/ceph-client/lib/vdso/datastore.c

## Purpose
Kernel-side storage and VVAR mapping support for generic vDSO data pages, including time data, RNG data, optional architecture data, dynamic page allocation, and page-fault mapping.

## APIs, Types, and Functions
Defines `vdso_k_time_data`, `vdso_k_rng_data`, and `vdso_k_arch_data` conditionally. Provides `vdso_setup_data_pages()`, `vvar_fault()`, `vdso_vvar_mapping`, and `vdso_install_vvar_mapping()`. Uses VDSO page offsets such as `VDSO_TIME_PAGE_OFFSET`, `VDSO_TIMENS_PAGE_OFFSET`, `VDSO_RNG_PAGE_OFFSET`, and architecture page ranges.

## Control Flow, State, and Persistence
Boot-time `vdso_initdata` holds initial page contents. `vdso_setup_data_pages()` allocates enough pages for `VDSO_NR_PAGES`, splits the allocation into individually refcounted pages, copies init data, and repoints exported kernel data pointers to the dynamic pages. `vvar_fault()` maps the requested VVAR page based on `vmf->pgoff`, handling time namespace special mapping by inserting the real time page at the namespace companion offset and returning the namespace page for the requested offset. Unsupported offsets or disabled features return `VM_FAULT_SIGBUS`. `vdso_install_vvar_mapping()` installs a sealed, read-only, IO, mixedmap special mapping.

## Dependencies and Integration
Depends on memory management, special mappings, time namespaces, `vdso/datapage.h`, and `linux/vdso_datastore.h`. It integrates with architecture vDSO setup and userspace VVAR fault handling.

## Risks and Test Signals
Risks include page-offset mismatches, time namespace double mapping mistakes, refcounting errors, panic on allocation failure, and assumptions about not using folios for namespace remapping. Test signals include VVAR fault tests for every offset, time namespace clock reads, mlockall behavior, unsupported config SIGBUS paths, and architecture data page ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/datastore.c -->
