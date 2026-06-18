<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor.h

Purpose: Provides inline C wrappers for PowerPC Ultravisor calls.

Important APIs/types/functions: `uv_register_pate()`, page share/unshare, page in/out, mem-slot register/unregister, invalidate, terminate, and PTCR fallback setup. Source-visible declarations include: #define _ASM_POWERPC_ULTRAVISOR_H; static inline void set_ptcr_when_no_uv(u64 val); static inline int uv_register_pate(u64 lpid, u64 dw0, u64 dw1); static inline int uv_share_page(u64 pfn, u64 npages); static inline int uv_unshare_page(u64 pfn, u64 npages); static inline int uv_unshare_all_pages(void); static inline int uv_page_in(u64 lpid, u64 src_ra, u64 dst_gpa, u64 flags,; static inline int uv_page_out(u64 lpid, u64 dst_ra, u64 src_gpa, u64 flags,.

Control flow: wrappers check firmware feature availability where needed and dispatch low-level ultravisor calls with typed arguments. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: secure memory sharing, mem slots, and PATE registration persist in ultravisor state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/asm-prototypes.h>, #include <asm/ultravisor-api.h>, #include <asm/firmware.h>. Integrated with secure guest/KVM memory management, pSeries firmware features, and ultravisor API constants.

Risks: missing firmware feature checks or wrong PFN/GPA arguments can leak protected pages or fail secure guests. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 85 lines, 2101 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor.h -->
