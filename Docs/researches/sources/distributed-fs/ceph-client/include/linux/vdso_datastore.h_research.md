# sources/distributed-fs/ceph-client/include/linux/vdso_datastore.h

## Purpose
This header declares generic vDSO data-page setup and VVAR mapping helpers.

## Important APIs, types, and functions
When `CONFIG_HAVE_GENERIC_VDSO` is enabled it exports `vdso_vvar_mapping`, `vdso_install_vvar_mapping()`, and `vdso_setup_data_pages()`. Disabled builds provide a no-op setup helper.

## Control flow, state, and persistence
Architecture or mm setup initializes vDSO data pages at boot and maps the VVAR special mapping into process address spaces. State is runtime memory mapping and vDSO data; no persistent storage is involved.

## Dependencies and integration points
It depends on mm types and integrates with architecture vDSO setup, mmap layout, timekeeping data exposure, and process exec/mmap paths.

## Risks and test signals
Risks include incorrect special mapping permissions, wrong address selection, and disabled-config differences. Tests should validate VVAR mapping presence, page permissions, vDSO time reads, and no-op setup on unsupported architectures.
