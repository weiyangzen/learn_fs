## sources/distributed-fs/ceph-client/arch/s390/kernel/uv.c

Purpose: Provides common s390 Ultravisor support for protected virtualization host/guest state, UV initialization, secure/shared page transitions, protected guest memory accessibility, UV capability/key sysfs exposure, and secret lookup/retrieval helpers.

Important APIs and functions: Exported state `prot_virt_guest`, `prot_virt_host`, `uv_info`; setup `setup_uv()`; page APIs `uv_pin_shared()`, `uv_destroy_folio()`, `uv_destroy_pte()`, `uv_convert_from_secure()`, `uv_convert_from_secure_folio()`, `uv_convert_from_secure_pte()`, `__make_folio_secure()`, `s390_wiggle_split_folio()`, `arch_make_folio_accessible()`; sysfs init `uv_sysfs_init()`; and secret APIs `uv_find_secret()` and `uv_retrieve_secret()`.

Control flow: Host setup reserves below-2GB UV base storage with memblock, issues `INIT_UV`, and disables host PV support on failure. Secure-page conversion functions iterate each base page in a folio and clear `PG_arch_1` on successful destroy/export. `__make_folio_secure()` verifies writeback/reference conditions, freezes expected references, sets `PG_arch_1`, issues a single UV call, unfreezes references, and maps UV condition codes to errno. `arch_make_folio_accessible()` treats `PG_arch_1` as a maybe-secure hint, first tries pin-shared, then convert-from-secure. Sysfs creates `/sys/firmware/uv` attributes for PV state, query data, optional key hashes, and secret capability information. Secret lookup pages through UV list results and retrieval maps return codes to stable Linux errors.

State and persistence: Boot-preserved UV state and `uv_info` are global. Folio `PG_arch_1` marks possible secure memory. Sysfs kobjects/ksets persist after device init. Secret buffers are caller-provided and ephemeral.

Dependencies and integration: Integrates with UV call ABI, memblock, folio/mm/pagewalk infrastructure, swap/writeback, KVM PV code, firmware sysfs, protected guest dump metadata, and s390 page-state/storage ownership rules.

Risks and test signals: Risks include folio reference-freeze races, large folio splitting/writeback retry behavior, stale `PG_arch_1` overindication, UV firmware return-code compatibility, and sysfs exposure only when facility 158 is present. Test signals include PV host boot with UV base allocation, KVM protected guest page import/export, swap/writeback of secure pages, sysfs `firmware/uv/*`, UV key query availability, and secret lookup/retrieve error mapping.
