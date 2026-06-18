<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/svm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/svm.h

Purpose: Exposes secure virtual machine guest detection and DTL cache constructor selection.

Important APIs/types/functions: `is_secure_guest()` and `get_dtl_cache_ctor()` conditional on `CONFIG_PPC_SVM`. Source-visible declarations include: #define _ASM_POWERPC_SVM_H; static inline bool is_secure_guest(void); #define get_dtl_cache_ctor() (is_secure_guest() ? dtl_cache_ctor : NULL); static inline bool is_secure_guest(void); #define get_dtl_cache_ctor() NULL.

Control flow: secure guest code tests MSR/firmware state and avoids normal dispatch trace log cache construction when encrypted isolation requires it. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: secure-guest state is CPU/firmware state, not stored here. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/reg.h>. Integrated with PowerPC secure VM, ultravisor, encrypted guest, and dispatch trace log code.

Risks: stubs must be false for non-SVM builds; secure guests must avoid sharing unsafe host-visible buffers. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 33 lines, 591 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/svm.h -->
