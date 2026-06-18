<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/security_features.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/security_features.h

Purpose: Defines the global bitmask and feature flags for PowerPC speculative-execution and cache-flush mitigations.

Important APIs/types/functions: `powerpc_security_features`, `security_ftr_set/clear/enabled()`, `enum stf_barrier_type`, and `SEC_FTR_*` mitigation bits. Source-visible declarations include: #define _ASM_POWERPC_SECURITY_FEATURES_H; extern u64 powerpc_security_features;; extern bool rfi_flush;; enum stf_barrier_type {; static inline void security_ftr_set(u64 feature); static inline void security_ftr_clear(u64 feature); static inline bool security_ftr_enabled(u64 feature); enum stf_barrier_type stf_barrier_type_get(void);.

Control flow: firmware/CPU discovery sets feature bits, mitigation code tests them, and patching code rewrites branches/barriers accordingly. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: the bitmask persists globally and controls runtime mitigation behavior. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with arch security setup, BPF JIT barriers, entry/exit mitigation code, and sysfs reporting.

Risks: bit semantics are security-sensitive; enabling too little exposes CPUs while enabling too much can cause severe performance loss. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 113 lines, 3509 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/security_features.h -->
