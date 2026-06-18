<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/page.h -->
# sources/distributed-fs/ceph-client/include/vdso/page.h

Purpose: defines page size, shift, and mask constants for vDSO code based on `CONFIG_PAGE_SHIFT`.

Important APIs and types: `PAGE_SHIFT`, `PAGE_SIZE`, and `PAGE_MASK` are defined with special handling for 32-bit architectures to avoid wrong sign/width extension.

Control flow: VVAR page sizing and symbol placement use these constants when aligning data pages and computing offsets.

State and persistence: no state; compile-time layout constants.

Dependencies and integration points: depends on UAPI const macros and kernel config. It integrates with `vdso/datapage.h` and linker script page calculations.

Risks and test signals: risks include incorrect mask width on 32-bit and mismatch with architecture page size. Test VVAR layout on 4K/16K/64K page configs and compat builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/page.h -->
