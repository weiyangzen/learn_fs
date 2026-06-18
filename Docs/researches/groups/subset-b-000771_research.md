# Research: subset-b-000771

Grouped research for PowerPC architecture headers under the ceph-client source tree, covering RTAS firmware interfaces, locking, SMP, SPU/Cell support, syscall and signal ABI, memory-management boundaries, text patching, user access, platform bridges, ultravisor/SVM, VAS, and vDSO support. Each section is keyed by the exact source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h

Purpose: Declares the relocatable heap allocator interface used by old PowerPC embedded drivers to manage scarce on-chip or bus-visible memory ranges.

Important APIs/types/functions: range block/list structures `rh_block_t`, allocator state `rh_info_t`, statistics `rh_stats_t`, allocation/alignment/free/grow helpers, and flags for static allocator metadata. Source-visible declarations include: #define __ASM_PPC_RHEAP_H__; typedef struct _rh_block {; struct list_head list;; typedef struct _rh_info {; struct list_head empty_list;; struct list_head free_list;; struct list_head taken_list;; #define RHIF_STATIC_INFO 0x1.

Control flow: callers initialize an `rh_info_t`, attach one or more free regions, allocate aligned ranges for hardware users, and return ranges to the free list; the header itself only declares the list-based state machine. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: free, empty, and taken lists persist inside the allocator object supplied by the caller. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/list.h>. Integrated with embedded communication and platform drivers that need physical-range allocation.

Risks: list corruption, overlapping region insertion, and static metadata lifetime mistakes can leak scarce hardware memory. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 92 lines, 2578 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h

Purpose: Provides the Freescale RapidIO machine-check hook surface.

Important APIs/types/functions: `fsl_rio_mcheck_exception(struct pt_regs *)`, compiled as a real declaration only when `CONFIG_FSL_RIO` is enabled. Source-visible declarations include: #define ASM_PPC_RIO_H; extern int fsl_rio_mcheck_exception(struct pt_regs *);; static inline int fsl_rio_mcheck_exception(struct pt_regs *regs) {return 0; }.

Control flow: machine-check handling can delegate RapidIO faults to this hook and otherwise gets a zero-return stub. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state in the header; platform RapidIO code owns any error registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC exception handling and Freescale RapidIO platform support.

Risks: the stub must preserve non-RIO builds while real handlers must classify machine checks without hiding unrelated CPU errors. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 18 lines, 424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h

Purpose: Defines the packed firmware data structures shared by RTAS core code, pSeries firmware calls, error logging, and hotplug/event handling.

Important APIs/types/functions: `rtas_arg_t`, `struct rtas_args`, `struct rtas_t`, `struct rtas_error_log`, `struct rtas_ext_event_log_v6`, `struct pseries_errorlog`, and hotplug log payload unions. Source-visible declarations include: #define _ASM_POWERPC_RTAS_TYPES_H; typedef __be32 rtas_arg_t;; struct rtas_args {; struct rtas_t {; struct device_node *dev; /* virtual address pointer */; struct rtas_error_log {; struct rtas_ext_event_log_v6 {; struct pseries_errorlog {.

Control flow: RTAS callers fill big-endian argument buffers and firmware writes status or event data into these structures. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serializes persistent firmware state and platform event records crossing the OS/firmware boundary. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler_attributes.h>. Integrated with PAPR RTAS firmware, pSeries error logging, event scan, hotplug, and sys_rtas paths.

Risks: all structure sizes, endian annotations, and packed layouts are ABI-sensitive firmware contracts. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 114 lines, 2910 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h

Purpose: Declares the allocator for RTAS firmware work areas that must be physically addressable and below RTAS placement limits.

Important APIs/types/functions: `struct rtas_work_area`, compile-time bounded `rtas_work_area_alloc()`, raw/size/physical accessors, free helpers, and arena reservation. Source-visible declarations include: #define _ASM_POWERPC_RTAS_WORK_AREA_H; struct rtas_work_area {; enum {; #define rtas_work_area_alloc(size_) ({ \; struct rtas_work_area *__rtas_work_area_alloc(size_t size);; static inline char *rtas_work_area_raw_buf(const struct rtas_work_area *area); static inline size_t rtas_work_area_size(const struct rtas_work_area *area); static inline phys_addr_t rtas_work_area_phys(const struct rtas_work_area *area).

Control flow: callers reserve the arena during boot, allocate a bounded work buffer, pass its physical address to firmware, then free the buffer. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: the arena is global reserved memory; each returned area tracks virtual buffer, size, and physical address. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/build_bug.h>, #include <linux/sizes.h>, #include <linux/types.h>, #include <asm/page.h>. Integrated with RTAS syscalls and firmware functions that require temporary data buffers.

Risks: sizes above the fixed limit are compile-time bugs and physical-address constraints must be preserved for firmware. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 96 lines, 2817 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h

Purpose: Main kernel interface for Run-Time Abstraction Services on CHRP and pSeries PowerPC systems.

Important APIs/types/functions: RTAS function handles/tokens, status constants, `rtas_call()`, unlocked call variants, busy-delay helpers, error-log helpers, flash/NVRAM/power/sensor/indicator APIs, syscall controls, and global RTAS state. Source-visible declarations include: #define _POWERPC_RTAS_H; enum rtas_function_index {; typedef struct {; #define rtas_fn_handle(x_) ((const rtas_fn_handle_t) { .index = x_, }); #define RTAS_FN_CHECK_EXCEPTION rtas_fn_handle(RTAS_FNIDX__CHECK_EXCEPTION); #define RTAS_FN_DISPLAY_CHARACTER rtas_fn_handle(RTAS_FNIDX__DISPLAY_CHARACTER); #define RTAS_FN_EVENT_SCAN rtas_fn_handle(RTAS_FNIDX__EVENT_SCAN); #define RTAS_FN_FREEZE_TIME_BASE rtas_fn_handle(RTAS_FNIDX__FREEZE_TIME_BASE).

Control flow: client code resolves firmware tokens, builds argument counts and outputs, serializes through RTAS locking when required, handles busy/extended delay statuses, and consumes firmware return words. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global RTAS metadata, lock state, reserved user region, event logs, and firmware tokens persist after early discovery. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/mutex.h>, #include <linux/spinlock.h>, #include <asm/page.h>, #include <asm/rtas-types.h>, #include <linux/time.h>, #include <linux/cpumask.h>. Integrated with pSeries platform setup, XICS, PCI config, NVRAM, RTC, reboot/poweroff, firmware flash, hotplug, event scan, and user `sys_rtas`.

Risks: firmware return codes are not Linux errno, calls may need retry delays, and argument/work-area layout mistakes can corrupt firmware-visible memory. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 579 lines, 24630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h

Purpose: Wraps POWER run-latch control for 64-bit kernels.

Important APIs/types/functions: `ppc64_runlatch_on()` and `ppc64_runlatch_off()` macros around low-level run-latch assembly helpers and MSR tracking. Source-visible declarations include: #define _ASM_POWERPC_RUNLATCH_H; extern void __ppc64_runlatch_on(void);; extern void __ppc64_runlatch_off(void);; #define ppc64_runlatch_off() \; #define ppc64_runlatch_on() \; #define ppc64_runlatch_on(); #define ppc64_runlatch_off().

Control flow: scheduler and idle paths toggle the latch only when thread state says the hardware bit needs changing. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is per-thread/per-CPU hardware run-latch status, not stored here. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC64 idle, scheduler, and performance/power-management code.

Risks: incorrect toggling wastes power or hurts performance and 32-bit/no-runlatch builds must remain no-ops. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 44 lines, 1180 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h

Purpose: Defines PowerPC seccomp audit architecture variants and sigreturn syscall names.

Important APIs/types/functions: native and compat seccomp syscall numbers, little-endian audit suffix fields, and generic seccomp inclusion. Source-visible declarations include: #define _ASM_POWERPC_SECCOMP_H; #define __NR_seccomp_sigreturn_32 __NR_sigreturn; #define __SECCOMP_ARCH_LE __AUDIT_ARCH_LE; #define __SECCOMP_ARCH_LE_NAME "le"; #define __SECCOMP_ARCH_LE 0; #define __SECCOMP_ARCH_LE_NAME.

Control flow: seccomp validation compares filter architecture values with task ABI and endian mode. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state; policy state lives in generic seccomp filters. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/unistd.h>, #include <asm-generic/seccomp.h>. Integrated with audit, ptrace, seccomp, and syscall ABI code.

Risks: audit constants must distinguish 32/64-bit and LE/BE ABIs or filters can match the wrong syscall table. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 34 lines, 1043 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sections.h

Purpose: Declares PowerPC linker-section symbols and helper predicates for text, init, exit, interrupt vectors, and patch sites.

Important APIs/types/functions: section boundary externs, `dereference_function_descriptor()`, text membership helpers, and branch-cache/security patch-site symbols. Source-visible declarations include: #define _ASM_POWERPC_SECTIONS_H; typedef struct func_desc func_desc_t;; extern char __head_end[];; extern char __srwx_boundary[];; extern char __exittext_begin[], __exittext_end[];; extern s32 patch__call_flush_branch_caches1;; extern s32 patch__call_flush_branch_caches2;; extern s32 patch__call_flush_branch_caches3;.

Control flow: runtime code tests addresses against section ranges and patching code resolves relative patch-site locations. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is linker-defined immutable address ranges and patch slots. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/elf.h>, #include <linux/uaccess.h>, #include <asm-generic/sections.h>. Integrated with module loader, ftrace/kprobes, instruction patching, exception text, and security mitigation patching.

Risks: section-boundary drift or function-descriptor confusion can make validators accept wrong addresses. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 83 lines, 2084 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h

Purpose: Exposes simple predicates for PowerPC secure boot and trusted boot support.

Important APIs/types/functions: `is_ppc_secureboot_enabled()` and `is_ppc_trustedboot_enabled()`. Source-visible declarations include: #define _ASM_POWER_SECURE_BOOT_H; static inline bool is_ppc_secureboot_enabled(void); static inline bool is_ppc_trustedboot_enabled(void).

Control flow: security and keyring code call these helpers and receive platform-specific answers only in secure-boot builds. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: boot trust state is platform state queried elsewhere; this wrapper stores none. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with platform security, module signature policy, and key-loading paths.

Risks: stubbed false values on unsupported builds must not be mistaken for a runtime disabled policy. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 29 lines, 476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h

Purpose: Defines the secure-variable backend operations used by PowerPC secure boot platforms.

Important APIs/types/functions: `struct secvar_operations`, global `secvar_ops`, and optional `set_secvar_ops()` registration. Source-visible declarations include: #define SECVAR_OPS_H; extern const struct secvar_operations *secvar_ops;; struct secvar_operations {; static inline int set_secvar_ops(const struct secvar_operations *ops) { return 0; }.

Control flow: a platform backend registers get/set/format/sysfs callbacks that higher-level secure variable code invokes. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: backend pointer and firmware variables persist globally once registered. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/errno.h>, #include <linux/sysfs.h>. Integrated with OPAL/pSeries secure-variable backends, sysfs, and secure boot policy code.

Risks: backend registration must be one-time and callbacks must validate firmware buffer sizes and permissions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 39 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h

Purpose: Provides PowerPC legacy serial-discovery declarations and default 8250 baud.

Important APIs/types/functions: `BASE_BAUD` and optional `find_legacy_serial_ports()`. Source-visible declarations include: #define _ASM_POWERPC_SERIAL_H; #define BASE_BAUD ( 1843200 / 16 ); extern void find_legacy_serial_ports(void);; #define find_legacy_serial_ports() do { } while (0).

Control flow: early platform setup calls the discovery hook when legacy serial support is built; other builds use a no-op macro. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serial port state is registered by platform code, not this header. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with 8250 discovery, early console, OF/platform serial setup.

Risks: legacy port probing can conflict with firmware-provided devices if discovery is enabled on the wrong platform. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h

Purpose: Declares PowerPC page-attribute change helpers for kernel text/data mappings.

Important APIs/types/functions: `set_memory_ro/rw/nx/x/np/p/rox()`, `set_memory_attr()`, and attribute operation codes. Source-visible declarations include: #define _ASM_POWERPC_SET_MEMORY_H; #define SET_MEMORY_RO 0; #define SET_MEMORY_RW 1; #define SET_MEMORY_NX 2; #define SET_MEMORY_X 3; #define SET_MEMORY_NP 4 /* Set memory non present */; #define SET_MEMORY_P 5 /* Set memory present */; #define SET_MEMORY_ROX 6.

Control flow: callers request page count and virtual address changes; MMU backend updates PTEs and flushes as needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: changes persist in kernel page tables until reversed. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with module loader, BPF/JIT, rodata hardening, text patching, and memory hotplug.

Risks: incorrect permission transitions can leave executable writable mappings or make live code/data inaccessible. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 51 lines, 1446 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h

Purpose: Declares the minimal PowerPC kernel setjmp/longjmp ABI.

Important APIs/types/functions: `JMP_BUF_LEN`, `jmp_buf`, `setjmp()`, and `longjmp()`. Source-visible declarations include: #define _ASM_POWERPC_SETJMP_H; #define JMP_BUF_LEN 23; typedef long jmp_buf[JMP_BUF_LEN];; extern int setjmp(jmp_buf env) __attribute__((returns_twice));; extern void longjmp(jmp_buf env, int val) __attribute__((noreturn));.

Control flow: low-level code snapshots nonlocal control-flow state and later restores it through assembly helpers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: jump buffers persist in caller-provided storage. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with xmon/debug and low-level recovery paths.

Risks: buffer length and saved register convention must match assembly or longjmp corrupts execution state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 15 lines, 400 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h

Purpose: Collects PowerPC setup-time declarations for relocation, memory limits, panic timeout, and platform init hooks.

Important APIs/types/functions: progress printing, `memory_limit`, relocation helpers, `initmem_init()`, pSeries relocation-on-exception helpers, KASLR init, and `ARCH_PANIC_TIMEOUT`. Source-visible declarations include: #define _ASM_POWERPC_SETUP_H; extern void ppc_printk_progress(char *s, unsigned short hex);; extern unsigned long long memory_limit;; struct device_node;; extern unsigned long reloc_offset(void);; extern unsigned long add_reloc_offset(unsigned long);; extern void reloc_got2(unsigned long);; #define PTRRELOC(x) ((typeof(x)) add_reloc_offset((unsigned long)(x))).

Control flow: early boot uses relocation helpers before final mappings and later platform setup queries feature hooks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: boot globals such as memory limit and relocation offset persist into setup. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/setup.h>. Integrated with early boot, pSeries, KASLR, memblock, console progress, and platform firmware discovery.

Risks: relocation helpers are valid only during boot phases where GOT/data relocation assumptions hold. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 99 lines, 2935 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h

Purpose: Supplies PowerPC machine definitions for the kernel soft-float implementation.

Important APIs/types/functions: word type sizes, multiply/divide meat macros, NaN bit patterns, exception flag mapping, rounding helpers, and endian-specific fraction packing. Source-visible declarations include: #define _FP_W_TYPE_SIZE 32; #define _FP_W_TYPE unsigned int; #define _FP_WS_TYPE signed int; #define _FP_I_TYPE int; #define __ll_B ((UWtype) 1 << (W_TYPE_SIZE / 2)); #define __ll_lowpart(t) ((UWtype) (t) & (__ll_B - 1)); #define __ll_highpart(t) ((UWtype) (t) >> (W_TYPE_SIZE / 2)); #define _FP_MUL_MEAT_S(R,X,Y) _FP_MUL_MEAT_1_wide(_FP_WFRACBITS_S,R,X,Y,umul_ppmm).

Control flow: soft-float routines expand these macros to implement IEEE operations without hardware FP. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is per-operation FP fragments and exception flags, not persistent header data. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/kernel.h>, #include <linux/sched.h>, #include <linux/types.h>, #include <asm/byteorder.h>. Integrated with Linux soft-fp library, math emulation, and no-FPU kernel paths.

Risks: rounding, endian packing, and exception flag definitions are numerically sensitive and require cross-endian tests. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 343 lines, 12676 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/shmparam.h

Purpose: Provides the PowerPC shared-memory parameter include point.

Important APIs/types/functions: include guard only in this snapshot, relying on generic defaults. Source-visible declarations include: #define _ASM_POWERPC_SHMPARAM_H.

Control flow: generic SysV shared memory code includes it for architecture overrides. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with SysV IPC and generic asm parameter inclusion.

Risks: minimal wrapper; adding overrides would affect user-visible shared-memory alignment. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 7 lines, 206 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/signal.h

Purpose: Connects kernel signal code to PowerPC UAPI signal and ptrace definitions.

Important APIs/types/functions: `__ARCH_HAS_SA_RESTORER`, `struct pt_regs` forward declaration, and UAPI includes. Source-visible declarations include: #define _ASM_POWERPC_SIGNAL_H; #define __ARCH_HAS_SA_RESTORER; struct pt_regs;.

Control flow: signal setup/return code uses UAPI layouts while generic code sees the arch restorer capability. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: signal frame state lives in user memory and task registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/signal.h>, #include <uapi/asm/ptrace.h>. Integrated with PowerPC signal delivery, compat signal handling, ptrace, and libc restorer ABI.

Risks: restorer and pt_regs ABI assumptions are user-visible and must match signal frame implementations. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 17 lines, 506 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h

Purpose: Implements the legacy PowerPC simple spinlock and rwlock primitives.

Important APIs/types/functions: lock token selection, `arch_spin_*`, `arch_read_*`, `arch_write_*`, paravirt yield hooks, ticketless wait loops, and memory-barrier usage. Source-visible declarations include: #define _ASM_POWERPC_SIMPLE_SPINLOCK_H; #define LOCK_TOKEN (*(u32 *)(&get_paca()->lock_token)); #define LOCK_TOKEN (*(u32 *)(&get_paca()->paca_index)); #define LOCK_TOKEN 1; static inline int arch_spin_is_locked(arch_spinlock_t *lock); static inline unsigned long __arch_spin_trylock(arch_spinlock_t *lock); static inline int arch_spin_trylock(arch_spinlock_t *lock); static inline void splpar_spin_yield(arch_spinlock_t *lock) {}.

Control flow: trylock uses atomic load/store reservation, lock paths spin with optional SPLPAR yield, and unlock stores zero with release ordering. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: lock word state is caller-owned and may encode CPU/PACA tokens. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/irqflags.h>, #include <linux/kcsan-checks.h>, #include <asm/paravirt.h>, #include <asm/paca.h>, #include <asm/synch.h>, #include <asm/ppc-opcode.h>. Integrated with locking core, paravirt/splpar yield, paca, low-level synchronization, and irq-safe sections.

Risks: barrier placement and token ownership are concurrency-critical; regressions deadlock under SMP or virtualized contention. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 268 lines, 6242 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h

Purpose: Defines the storage layout for PowerPC simple spinlocks and rwlocks.

Important APIs/types/functions: `arch_spinlock_t`, `arch_rwlock_t`, and unlocked initializers. Source-visible declarations include: #define _ASM_POWERPC_SIMPLE_SPINLOCK_TYPES_H; typedef struct {; #define __ARCH_SPIN_LOCK_UNLOCKED { 0 }; typedef struct {; #define __ARCH_RW_LOCK_UNLOCKED { 0 }.

Control flow: included before primitive implementations and by lockdep/generic lock code. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: lock values persist in the object embedding these types. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with simple spinlock backend selected when queued locks are disabled.

Risks: type layout is ABI for assembly/inlines and must match lock algorithms. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 487 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h

Purpose: Declares PowerPC SMP topology, CPU bring-up, IPI, NMI, and CPU mask helpers.

Important APIs/types/functions: boot CPU IDs, `struct smp_ops_t`, CPU maps, IPI message enums, kick/offline hooks, NMI helpers, and topology mask accessors. Source-visible declarations include: #define _ASM_POWERPC_SMP_H; extern int boot_cpuid;; extern int boot_cpu_hwid; /* PPC64 only */; extern int boot_core_hwid;; extern int spinning_secondaries;; extern u32 *cpu_to_phys_id;; extern bool coregroup_enabled;; extern int cpu_to_chip_id(int cpu);.

Control flow: platform code fills `smp_ops`, boot code releases secondary CPUs, and runtime code sends IPIs or queries sibling/core masks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global CPU maps, boot CPU IDs, and per-CPU topology masks persist after discovery. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/threads.h>, #include <linux/cpumask.h>, #include <linux/kernel.h>, #include <linux/irqreturn.h>, #include <asm/paca.h>, #include <asm/percpu.h>. Integrated with scheduler topology, hotplug, interrupt controller code, KVM, and platform CPU bring-up.

Risks: CPU numbering versus hardware IDs is subtle, and hotplug/IPI ordering bugs can hang secondary CPUs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 272 lines, 7179 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h

Purpose: Defines the Apple System Management Unit command interface and request structures.

Important APIs/types/functions: SMU command IDs, transfer flags, `struct smu_cmd`, async request queues, partition/RTC/I2C/fan/LED/battery helpers, and platform init declarations. Source-visible declarations include: #define _SMU_H; #define SMU_CMD_PARTITION_COMMAND 0x3e; #define SMU_CMD_PARTITION_LATEST 0x01; #define SMU_CMD_PARTITION_BASE 0x02; #define SMU_CMD_PARTITION_UPDATE 0x03; #define SMU_CMD_FAN_COMMAND 0x4a; #define SMU_CMD_BATTERY_COMMAND 0x6f; #define SMU_CMD_GET_BATTERY_INFO 0x00.

Control flow: callers prepare a command buffer, submit sync or async requests, and callbacks consume firmware replies. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: request objects, command buffers, SMU firmware state, and sysfs-visible device state persist outside this header. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/list.h>, #include <linux/types.h>. Integrated with PowerMac thermal, fan, RTC, I2C, LED, battery, and reboot/power-control code.

Risks: firmware command lengths and callback lifetimes are fragile; bad commands can stall platform management. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 694 lines, 19789 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h

Purpose: Sets PowerPC sparsemem section sizing and hotplug NUMA helpers.

Important APIs/types/functions: `SECTION_SIZE_BITS`, optional `MAX_PHYSMEM_BITS`, `remove_section_mapping()`, `memory_add_physaddr_to_nid()`, and `hot_add_scn_to_nid()`. Source-visible declarations include: #define _ASM_POWERPC_SPARSEMEM_H 1; #define SECTION_SIZE_BITS 24; extern int remove_section_mapping(unsigned long start, unsigned long end);; extern int memory_add_physaddr_to_nid(u64 start);; #define memory_add_physaddr_to_nid memory_add_physaddr_to_nid; extern int hot_add_scn_to_nid(unsigned long scn_addr);; static inline int hot_add_scn_to_nid(unsigned long scn_addr).

Control flow: memory hotplug code maps physical sections to nodes and tears down section mappings. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: memory section/node mappings persist in sparsemem metadata. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with memory hotplug, NUMA, memblock, and sparsemem core.

Risks: section-size constants shape the memmap ABI and hotplug helpers must match firmware topology. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h

Purpose: Selects the configured PowerPC spinlock implementation and supplies the post-lock memory barrier.

Important APIs/types/functions: queued spin/rwlock includes when enabled, simple spinlock fallback, `smp_mb__after_spinlock()`, and `pv_spinlocks_init()`. Source-visible declarations include: #define __ASM_SPINLOCK_H; #define smp_mb__after_spinlock() smp_mb(); static inline void pv_spinlocks_init(void) { }.

Control flow: generic locking includes this header to bind arch lock operations. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state lives in selected lock types. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/qspinlock.h>, #include <asm/qrwlock.h>, #include <asm/simple_spinlock.h>. Integrated with locking core, qspinlock, qrwlock, paravirt, and simple spinlock code.

Risks: backend selection must keep type and operation headers consistent across configs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock_types.h

Purpose: Selects the configured PowerPC spinlock type definitions.

Important APIs/types/functions: queued spinlock/qrwlock type includes or simple spinlock type fallback. Source-visible declarations include: #define _ASM_POWERPC_SPINLOCK_TYPES_H.

Control flow: included by generic spinlock types before operation headers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: lock storage is embedded in users of the types. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/qspinlock_types.h>, #include <asm-generic/qrwlock_types.h>, #include <asm/simple_spinlock_types.h>. Integrated with generic locking and architecture lock backend selection.

Risks: mismatched type/backend configuration breaks every spinlock user at compile or runtime. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 16 lines, 380 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h

Purpose: Main kernel interface for Cell Broadband Engine Synergistic Processing Units and spufs.

Important APIs/types/functions: MFC command/event constants, `struct spu`, `struct cbe_spu_info`, SPU callbacks, runqueue/context declarations, syscall/coredump hooks, and SPU MMU helpers. Source-visible declarations include: #define _SPU_H; #define LS_SIZE (256 * 1024); #define LS_ADDR_MASK (LS_SIZE - 1); #define MFC_PUT_CMD 0x20; #define MFC_PUTS_CMD 0x28; #define MFC_PUTR_CMD 0x30; #define MFC_PUTF_CMD 0x22; #define MFC_PUTB_CMD 0x21.

Control flow: platform code discovers SPUs, spufs binds contexts to SPUs, interrupt callbacks handle mailbox/MFC/stop events, and MM code flushes SPU SLBs. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: persistent SPU device objects track local store, MM association, interrupts, callbacks, runqueue state, owner PIDs, and utilization stats. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/workqueue.h>, #include <linux/device.h>, #include <linux/mutex.h>, #include <asm/reg.h>, #include <asm/copro.h>. Integrated with Cell platform setup, spufs, scheduler, coredumps, MMU/SLB handling, IRQ affinity, and coprocessor support.

Risks: hardware register ordering, context-switch flags, and callback lifetimes are hard to test without Cell hardware. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 679 lines, 23975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h

Purpose: Defines the SPU context save area layout and register save/restore status codes.

Important APIs/types/functions: SPU GPR/SPR counts, save/restore magic values, stopped-status constants, and `struct spu_lscsa`-style local-store save layout definitions. Source-visible declarations include: #define _SPU_CSA_H_; #define NR_SPU_GPRS 128; #define NR_SPU_SPRS 9; #define NR_SPU_REGS_PAD 7; #define NR_SPU_SPILL_REGS 144 /* GPRS + SPRS + PAD */; #define SIZEOF_SPU_SPILL_REGS NR_SPU_SPILL_REGS * 16; #define SPU_SAVE_COMPLETE 0x3FFB; #define SPU_RESTORE_COMPLETE 0x3FFC.

Control flow: SPU context switch code uses these layouts to save local store and architectural state between contexts. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: context save areas persist per SPU context and may be consumed by coredumps or restore code. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with spufs context switching, Cell low-level save/restore assembly, and coredump support.

Risks: layout and alignment must match SPU microcode/assembly expectations or context restore corrupts user state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 247 lines, 6167 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_csa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h

Purpose: Includes kernel SPU definitions and the UAPI SPU info structures in one internal header.

Important APIs/types/functions: `asm/spu.h` plus `uapi/asm/spu_info.h`. Source-visible declarations include: #define _SPU_INFO_H.

Control flow: spufs and coredump paths include it when both kernel state and user-visible info records are needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state beyond included structures. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/spu.h>, #include <uapi/asm/spu_info.h>. Integrated with Cell spufs, proc/debug info, and UAPI reporting.

Risks: wrapper must not create conflicting definitions between kernel-only and UAPI SPU structures. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 15 lines, 272 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h

Purpose: Defines the privileged SPU register operation dispatch table.

Important APIs/types/functions: `struct spu_priv1_ops`, global `spu_priv1_ops`, and inline wrappers for interrupt mask/stat, MFC SR1, SPU run control, status, and TLB invalidation. Source-visible declarations include: #define _SPU_PRIV1_H; struct spu;; struct spu_context;; struct spu_priv1_ops {; extern const struct spu_priv1_ops* spu_priv1_ops;; static inline void; static inline void; static inline void.

Control flow: platform-specific backend operations are installed and generic SPU code invokes them through wrappers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: backend pointer persists globally; hardware state is in privileged SPU registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with native Cell, hypervisor/Beat SPU backends, and SPU interrupt/MMU control.

Risks: a missing backend or wrong op ordering breaks privileged SPU control and can lose interrupts. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 221 lines, 5077 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h

Purpose: Declares PowerPC instruction single-step analysis and emulation metadata.

Important APIs/types/functions: instruction-type enum, flag bits, `struct instruction_op`, register-name helpers, `analyse_instr()`, `emulate_step()`, and related emulate helpers. Source-visible declarations include: struct pt_regs;; #define IS_MTMSRD(instr) ((ppc_inst_val(instr) & 0xfc0007be) == 0x7c000124); #define IS_RFID(instr) ((ppc_inst_val(instr) & 0xfc0007be) == 0x4c000024); enum instruction_type {; #define INSTR_TYPE_MASK 0x1f; #define OP_IS_LOAD(type) ((LOAD <= (type) && (type) <= LOAD_VSX) || (type) == LARX); #define OP_IS_STORE(type) ((STORE <= (type) && (type) <= STORE_VSX) || (type) == STCX); #define OP_IS_LOAD_STORE(type) (LOAD <= (type) && (type) <= STCX).

Control flow: debug/kprobe/single-step code decodes one instruction, classifies memory/control effects, and emulates or advances registers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: transient operation descriptions and pt_regs mutations are caller-owned. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/inst.h>. Integrated with kprobes, uprobes, xmon, ptrace single-step, and `lib/sstep.c` tests.

Risks: decoder coverage is large and ABI-sensitive; wrong classification can corrupt registers or skip faults. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 176 lines, 4713 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h

Purpose: Seeds the PowerPC per-task stack canary from early random data.

Important APIs/types/functions: `boot_init_stack_canary()` inline setup using `get_random_canary()`, current task, and paca canary state. Source-visible declarations include: #define _ASM_STACKPROTECTOR_H.

Control flow: boot and fork paths initialize stack canaries before protected C code relies on them. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: canary values persist per task and in PACA on 64-bit. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/reg.h>, #include <asm/current.h>, #include <asm/paca.h>. Integrated with compiler stack protector, task setup, current/PACA accessors, and random canary source.

Risks: must run early enough and update the right per-CPU/task storage or stack protector checks become ineffective. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 604 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h

Purpose: Provides the PowerPC stacktrace include point.

Important APIs/types/functions: include guard only in this snapshot. Source-visible declarations include: #define _ASM_POWERPC_STACKTRACE_H.

Control flow: generic stacktrace code includes it for architecture hooks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with unwinder and generic stacktrace infrastructure.

Risks: minimal wrapper; future hooks must align with PowerPC frame layout. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 13 lines, 297 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h

Purpose: Defines PowerPC static-call trampoline assembly layout.

Important APIs/types/functions: `ARCH_DEFINE_STATIC_CALL_TRAMP()`, null and ret0 trampolines, trampoline offsets, and call instruction size. Source-visible declarations include: #define _ASM_POWERPC_STATIC_CALL_H; #define __PPC_SCT(name, inst) \; #define PPC_SCT_RET0 20 /* Offset of label 1 */; #define PPC_SCT_DATA 28 /* Offset of label 2 */; #define ARCH_DEFINE_STATIC_CALL_TRAMP(name, func) __PPC_SCT(name, "b " #func); #define ARCH_DEFINE_STATIC_CALL_NULL_TRAMP(name) __PPC_SCT(name, "blr"); #define ARCH_DEFINE_STATIC_CALL_RET0_TRAMP(name) __PPC_SCT(name, "b .+20"); #define CALL_INSN_SIZE 4.

Control flow: static-call core emits or patches trampoline text using fixed offset labels. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is generated executable trampoline text. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with kernel static call core and PowerPC text patching.

Risks: hard-coded offsets must match emitted assembly exactly or runtime patching edits the wrong instruction. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 31 lines, 1090 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h

Purpose: Declares PowerPC optimized string and memory primitives.

Important APIs/types/functions: `__HAVE_ARCH_*` feature macros and prototypes for strcpy/strncpy/strcmp/memset/memcpy/memmove/memchr/memcmp plus flushcache copy. Source-visible declarations include: #define _ASM_POWERPC_STRING_H; #define __HAVE_ARCH_STRNCPY; #define __HAVE_ARCH_STRNCMP; #define __HAVE_ARCH_MEMCHR; #define __HAVE_ARCH_MEMCMP; #define __HAVE_ARCH_MEMSET16; #define __HAVE_ARCH_MEMSET; #define __HAVE_ARCH_MEMCPY.

Control flow: generic lib/string uses these arch hooks when available. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state; operations mutate caller buffers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with kernel lib/string, memcpy flushcache users, and assembly string implementations.

Risks: prototype drift or wrong arch-hook macros can select incompatible optimized routines. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 92 lines, 2870 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swab.h

Purpose: Routes PowerPC byte-swap support to the UAPI swab definitions.

Important APIs/types/functions: `uapi/asm/swab.h` include. Source-visible declarations include: #define _ASM_POWERPC_SWAB_H.

Control flow: generic byte-order helpers include this arch wrapper. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/swab.h>. Integrated with kernel and exported byte-swap helpers.

Risks: minimal wrapper; accelerated UAPI assembly must compile across endian/config variants. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 9 lines, 173 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h

Purpose: Declares PowerPC SWIOTLB enable flags and 4G detection hook.

Important APIs/types/functions: `ppc_swiotlb_enable`, `ppc_swiotlb_flags`, and optional `swiotlb_detect_4g()`. Source-visible declarations include: #define __ASM_SWIOTLB_H; extern unsigned int ppc_swiotlb_enable;; extern unsigned int ppc_swiotlb_flags;; static inline void swiotlb_detect_4g(void) {}.

Control flow: DMA setup decides whether to force bounce buffering and sets SWIOTLB flags before devices probe. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global SWIOTLB enable/flag state persists after boot. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/swiotlb.h>. Integrated with DMA mapping, memory encryption/secure guest paths, and generic SWIOTLB.

Risks: incorrect detection causes devices to DMA above their addressing limits or needlessly bounce all DMA. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 20 lines, 413 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h

Purpose: Declares PowerPC context-switch and lazy processor-state restore hooks.

Important APIs/types/functions: `__switch_to`, `_switch`, `switch_to` macro, debug register switch, math/vector/VSX/SPE/TM restore helpers, and `flush_all_to_thread()`. Source-visible declarations include: #define _ASM_POWERPC_SWITCH_TO_H; struct thread_struct;; struct task_struct;; struct pt_regs;; extern struct task_struct *__switch_to(struct task_struct *,; struct task_struct *);; #define switch_to(prev, next, last) ((last) = __switch_to((prev), (next))); extern struct task_struct *_switch(struct thread_struct *prev,.

Control flow: scheduler switches task_struct/thread state, then lazy restore paths reload math/vector/debug/TM state as needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: per-thread CPU extended state persists in `thread_struct` and hardware registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sched.h>, #include <asm/reg.h>. Integrated with scheduler, ptrace, signal, KVM, debug registers, FPU/Altivec/VSX/SPE, and transactional memory.

Risks: lazy restore and flush ordering are correctness-critical for ptrace, signal frames, and context isolation. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 133 lines, 3230 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h

Purpose: Defines PowerPC memory synchronization instructions and barrier string macros.

Important APIs/types/functions: `eieio()`, `isync()`, `ppc_after_tlbiel_barrier()`, lwsync fixups, acquire/release barrier strings, and atomic entry/exit barriers. Source-visible declarations include: #define _ASM_POWERPC_SYNCH_H; extern unsigned int __start___lwsync_fixup, __stop___lwsync_fixup;; extern void do_lwsync_fixups(unsigned long value, void *fixup_start,; static inline void eieio(void); static inline void isync(void); static inline void ppc_after_tlbiel_barrier(void); #define __PPC_ACQUIRE_BARRIER \; #define PPC_ACQUIRE_BARRIER "\n" stringify_in_c(__PPC_ACQUIRE_BARRIER).

Control flow: atomic/locking/TLB code emits the selected barrier sequence, with boot-time fixups replacing unsupported lwsync forms. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: patchable barrier sites are linker/runtime state; no per-call state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/cputable.h>, #include <asm/feature-fixups.h>, #include <asm/ppc-opcode.h>. Integrated with atomic primitives, spinlocks, TLB invalidation, feature fixups, and assembly code.

Risks: barrier weakening can create rare memory-order bugs; CPU feature fixups must match hardware support. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 73 lines, 2159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h

Purpose: Implements PowerPC syscall tracing helpers over `pt_regs`.

Important APIs/types/functions: syscall function pointer type, syscall tables, get/set syscall number, rollback, return/error extraction, argument get/set, and audit architecture selection. Source-visible declarations include: #define _ASM_SYSCALL_H 1; typedef long (*syscall_fn)(const struct pt_regs *);; typedef long (*syscall_fn)(unsigned long, unsigned long, unsigned long,; extern const syscall_fn sys_call_table[];; extern const syscall_fn compat_sys_call_table[];; static inline int syscall_get_nr(struct task_struct *task, struct pt_regs *regs); static inline void syscall_set_nr(struct task_struct *task, struct pt_regs *regs, int nr); static inline void syscall_rollback(struct task_struct *task,.

Control flow: ptrace/seccomp/audit code inspects or rewrites pt_regs before/after syscall dispatch. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is task pt_regs and syscall table selection. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/linux/audit.h>, #include <linux/sched.h>, #include <linux/thread_info.h>. Integrated with syscall entry, audit, seccomp, ptrace, tracing, and compat syscall handling.

Risks: argument register order and error conventions differ across ABIs; mistakes break tracers and filters. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 142 lines, 3607 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h

Purpose: Defines PowerPC syscall wrapper macros that unpack `pt_regs` into typed syscall arguments.

Important APIs/types/functions: `SC_POWERPC_REGS_TO_ARGS`, `__SYSCALL_DEFINEx`, `SYSCALL_DEFINE0`, and `COND_SYSCALL()`. Source-visible declarations include: #define __ASM_POWERPC_SYSCALL_WRAPPER_H; struct pt_regs;; #define SC_POWERPC_REGS_TO_ARGS(x, ...) \; #define __SYSCALL_DEFINEx(x, name, ...) \; static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__)); \; static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__)); #define SYSCALL_DEFINE0(sname) \; #define COND_SYSCALL(name) \.

Control flow: macro expansion emits wrapper, alias, metadata, and inline typed implementation for syscall table entries. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no runtime state beyond generated functions. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with generic syscall definition machinery and PowerPC pt_regs ABI.

Risks: macro signature changes can break syscall metadata, tracing, or compat builds. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 49 lines, 1670 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h

Purpose: Declares PowerPC-specific syscall entry points and builds syscall table declarations.

Important APIs/types/functions: compat/native syscall prototypes, `merge_64()`, PowerPC special syscalls, conditional table declarations, and syscall table includes. Source-visible declarations include: #define __ASM_POWERPC_SYSCALLS_H; struct rtas_args;; #define merge_64(low, high) (((u64)high << 32) | low); #define merge_64(high, low) (((u64)high << 32) | low); struct ucontext __user *new_ctx, long ctx_size);; struct sig_dbg_op __user *dbg);; struct ucontext32 __user *new_ctx,; struct compat_rlimit __user *rlim);.

Control flow: generated syscall-table macros expand to external declarations or table entries depending on config. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: syscall tables are immutable dispatch state after build/link. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/linkage.h>, #include <linux/types.h>, #include <linux/compat.h>, #include <asm/syscall.h>, #include <asm/syscalls_32.h>, #include <asm/unistd.h>, #include <asm/ucontext.h>. Integrated with syscall dispatch, compat layer, signal/ucontext, RTAS, ppc64/personality, and generated syscall tables.

Risks: prototype and argument-order mismatches are ABI-breaking, especially 32-bit split 64-bit arguments. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 161 lines, 5171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h

Purpose: Defines 32-bit PowerPC signal/ucontext compatibility structures used by syscall prototypes.

Important APIs/types/functions: `pt_regs32`, `sigcontext32`, `mcontext32`, and `ucontext32`. Source-visible declarations include: #define _ASM_POWERPC_SYSCALLS_32_H; struct pt_regs32 {; struct sigcontext32 {; struct mcontext32 {; struct ucontext32 {; struct mcontext32 uc_mcontext;.

Control flow: compat syscall and signal code copy these layouts to and from 32-bit user memory. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: user signal/ucontext frames persist across signal delivery and sigreturn. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compat.h>, #include <asm/siginfo.h>, #include <asm/signal.h>. Integrated with 32-bit PowerPC ABI, compat signal handling, and ptrace/syscall code.

Risks: field order and sizes are user ABI and must match libc/kernel signal expectations. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 60 lines, 1618 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h

Purpose: Defines the ppc64 system configuration page exported to userspace.

Important APIs/types/functions: `SYSTEMCFG_MAJOR/MINOR`, `struct systemcfg`, and global `systemcfg` pointer. Source-visible declarations include: #define _SYSTEMCFG_H; #define SYSTEMCFG_MAJOR 1; #define SYSTEMCFG_MINOR 1; struct systemcfg {; struct { /* Systemcfg version numbers */; extern struct systemcfg *systemcfg;.

Control flow: kernel populates the page with processor, cache, TB, platform, and feature data for userspace/vDSO consumers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: the mapped systemcfg page persists as read-mostly kernel/userspace ABI state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with ppc64 vDSO, glibc, timebase calibration, and platform feature discovery.

Risks: layout changes require versioning and userspace compatibility care. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 52 lines, 1726 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h

Purpose: Computes 32-bit PowerPC user, module, vmalloc, and IO mapping address windows.

Important APIs/types/functions: `MODULES_*`, `USER_TOP`, `TASK_SIZE`, `VMALLOC_START/END`, `IOREMAP_TOP`, and config-dependent layout constants. Source-visible declarations include: #define _ASM_POWERPC_TASK_SIZE_32_H; #define MODULES_END ASM_CONST(CONFIG_PAGE_OFFSET); #define MODULES_SIZE (CONFIG_MODULES_SIZE * SZ_1M); #define MODULES_VADDR (MODULES_END - MODULES_SIZE); #define MODULES_BASE (MODULES_VADDR & ~(UL(SZ_4M) - 1)); #define USER_TOP (MODULES_BASE - SZ_4M); #define MODULES_END (ASM_CONST(CONFIG_PAGE_OFFSET) & ~(UL(SZ_256M) - 1)); #define MODULES_SIZE (CONFIG_MODULES_SIZE * SZ_1M).

Control flow: MM setup and address validation use these constants to split user, module, vmalloc, and ioremap spaces. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: layout persists as the process/kernel virtual address ABI for the booted config. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sizes.h>. Integrated with 32-bit MMU setup, modules, vmalloc, ioremap, and `access_ok()`.

Risks: small layout changes can overlap user space, modules, or vmalloc and break ABI assumptions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 47 lines, 1345 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h

Purpose: Computes 64-bit PowerPC user address-space windows for hash/radix MMUs.

Important APIs/types/functions: 64TB through 4PB constants, `TASK_SIZE_USER64`, default map windows, context size, and 32-bit compatibility window. Source-visible declarations include: #define _ASM_POWERPC_TASK_SIZE_64_H; #define TASK_SIZE_64TB (0x0000400000000000UL); #define TASK_SIZE_128TB (0x0000800000000000UL); #define TASK_SIZE_512TB (0x0002000000000000UL); #define TASK_SIZE_1PB (0x0004000000000000UL); #define TASK_SIZE_2PB (0x0008000000000000UL); #define TASK_SIZE_4PB (0x0010000000000000UL); #define TASK_SIZE_USER64 TASK_SIZE_4PB.

Control flow: MM code chooses effective user/task size from MMU mode, CPU features, and process ABI. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: virtual address limits persist per process/mm context. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with 64-bit MM, mmap layout, radix/hash MMU, compat tasks, and user access checks.

Risks: expanding windows affects userspace ABI, pointer tagging assumptions, and context-ID sizing. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 83 lines, 2630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h

Purpose: Defines Translation Control Entry constants for PowerPC IOMMU tables.

Important APIs/types/functions: TCE types, entry size, valid/all-LPAR/read/write bits for PCI and virtual bus. Source-visible declarations include: #define _ASM_POWERPC_TCE_H; #define TCE_VB 0; #define TCE_PCI 1; #define TCE_ENTRY_SIZE 8 /* each TCE is 64 bits */; #define TCE_VALID 0x800 /* TCE valid */; #define TCE_ALLIO 0x400 /* TCE valid for all lpars */; #define TCE_PCI_WRITE 0x2 /* write from PCI allowed */; #define TCE_PCI_READ 0x1 /* read from PCI allowed */.

Control flow: IOMMU code composes TCE words to map DMA addresses for devices or virtual buses. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: TCE tables persist as hardware DMA translation state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/iommu.h>. Integrated with pSeries IOMMU, PCI DMA mapping, virtual bus DMA, and hypervisor TCE calls.

Risks: wrong permission bits can expose memory to devices or break DMA. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 892 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h

Purpose: Declares and partially implements PowerPC runtime instruction patching helpers.

Important APIs/types/functions: branch creation/validation, `patch_instruction*`, `patch_instructions()`, site-address helpers, data patch helpers, feature-section patching, and instruction comparison helpers. Source-visible declarations include: #define _ASM_POWERPC_CODE_PATCHING_H; #define BRANCH_SET_LINK 0x1; #define BRANCH_ABSOLUTE 0x2; static inline bool is_offset_in_branch_range(long offset); static inline bool is_offset_in_cond_branch_range(long offset); static inline int create_branch(ppc_inst_t *instr, const u32 *addr,; #define patch_u64 patch_ulong; static inline int patch_uint(void *addr, unsigned int val).

Control flow: callers compute patch-site addresses, synthesize PowerPC instructions, patch text, and rely on cache/TLB synchronization in the implementation. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: patched kernel text and patch metadata persist after boot/runtime modification. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/types.h>, #include <asm/ppc-opcode.h>, #include <linux/string.h>, #include <linux/kallsyms.h>, #include <asm/asm-compat.h>, #include <asm/inst.h>. Integrated with ftrace, jump labels, static calls, alternatives, security mitigations, modules, BPF JIT, and feature fixups.

Risks: branch range checks, endianness, prefixed instructions, and cache synchronization are critical to avoid executing torn text. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 275 lines, 7542 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h

Purpose: Defines low-level PowerPC thread-info layout, flags, stack sizing, and syscall-work masks.

Important APIs/types/functions: `THREAD_SIZE`, `THREAD_ALIGN`, `struct thread_info`, `INIT_THREAD_INFO`, TIF bits, local flags, and work-mask macros. Source-visible declarations include: #define _ASM_POWERPC_THREAD_INFO_H; #define MIN_THREAD_SHIFT (CONFIG_THREAD_SHIFT + 1); #define MIN_THREAD_SHIFT CONFIG_THREAD_SHIFT; #define THREAD_SHIFT PAGE_SHIFT; #define THREAD_SHIFT MIN_THREAD_SHIFT; #define THREAD_SIZE (1 << THREAD_SHIFT); #define THREAD_ALIGN_SHIFT (THREAD_SHIFT + 1); #define THREAD_ALIGN_SHIFT THREAD_SHIFT.

Control flow: entry assembly and scheduler test flags to decide syscall tracing, signal delivery, reschedule, restore, and mitigation work. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: thread_info persists at the task stack/thread base and is read by assembly. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/asm-const.h>, #include <asm/page.h>, #include <linux/cache.h>, #include <asm/processor.h>, #include <asm/accounting.h>, #include <asm/ppc_asm.h>. Integrated with entry/exit assembly, scheduler, signal, seccomp, livepatch, KVM, and stack allocation.

Risks: flag numbers and struct offsets are assembly ABI; changing them requires offset regeneration and entry-path tests. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 238 lines, 7798 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h

Purpose: Declares PowerPC timebase, decrementer, clockevent, and VDSO timekeeping interfaces.

Important APIs/types/functions: timebase frequencies, decrementer globals, calibration functions, RTC and clockevent hooks, `get_tbl()`, `get_tb()`, and VDSO timebase include. Source-visible declarations include: #define __POWERPC_TIME_H; extern u64 decrementer_max;; extern unsigned long tb_ticks_per_jiffy;; extern unsigned long tb_ticks_per_usec;; extern unsigned long tb_ticks_per_sec;; extern struct clock_event_device decrementer_clockevent;; extern u64 decrementer_max;; extern void generic_calibrate_decr(void);.

Control flow: boot calibrates timebase/decrementer, timer interrupt code programs decrementer, and readers fetch TB values for clocks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: frequency globals and boot timebase persist as calibration state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/percpu.h>, #include <asm/processor.h>, #include <asm/cpu_has_feature.h>, #include <asm/vdso/timebase.h>. Integrated with timekeeping, clocksource/clockevent, pSeries/PPC RTC, vDSO, and scheduler ticks.

Risks: timebase frequency mismatches cause clock drift and decrementer wrap/max handling is CPU-specific. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 120 lines, 2949 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/timex.h

Purpose: Defines PowerPC generic cycle-counter hooks.

Important APIs/types/functions: `CLOCK_TICK_RATE`, `cycles_t`, `get_cycles()`, and `random_get_entropy`. Source-visible declarations include: #define _ASM_POWERPC_TIMEX_H; #define CLOCK_TICK_RATE 1024000 /* Underlying HZ */; typedef unsigned long cycles_t;; static inline cycles_t get_cycles(void); #define get_cycles get_cycles.

Control flow: generic time and entropy code reads the timebase through the VDSO helper path. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state beyond hardware timebase. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/cputable.h>, #include <asm/vdso/timebase.h>. Integrated with timekeeping, scheduler clock, entropy, and VDSO timebase.

Risks: timebase availability and CPU feature checks must match early boot and suspend/resume behavior. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 25 lines, 463 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h

Purpose: Adapts generic TLB gather to PowerPC MMU behavior.

Important APIs/types/functions: `__tlb_remove_tlb_entry()`, `tlb_flush()`, `tlb_needs_table_invalidate()`, and local/thread/core MM helpers. Source-visible declarations include: #define _ASM_POWERPC_TLB_H; static inline void __tlb_remove_tlb_entry(struct mmu_gather *tlb, pte_t *ptep,; #define __tlb_remove_tlb_entry __tlb_remove_tlb_entry; #define tlb_flush tlb_flush; extern void tlb_flush(struct mmu_gather *tlb);; #define tlb_needs_table_invalidate() radix_enabled(); static inline void __tlb_remove_tlb_entry(struct mmu_gather *tlb, pte_t *ptep,; static inline int mm_is_core_local(struct mm_struct *mm).

Control flow: MM teardown batches PTE removals and later flushes translations with radix/hash-specific invalidation behavior. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: TLB gather state is caller-owned; hardware TLB state is invalidated by backend calls. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/pgtable.h>, #include <asm/page.h>, #include <asm/mmu.h>, #include <linux/pagemap.h>, #include <asm-generic/tlb.h>. Integrated with generic MM, radix/hash MMU, page-table freeing, and memory reclaim.

Risks: under-invalidating leaves stale translations while table invalidation requirements differ by MMU. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 93 lines, 2322 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlbflush.h

Purpose: Selects the Book3S or nohash PowerPC TLB flush implementation.

Important APIs/types/functions: `asm/book3s/tlbflush.h` or `asm/nohash/tlbflush.h` include selection. Source-visible declarations include: #define _ASM_POWERPC_TLBFLUSH_H.

Control flow: architecture MM code includes this wrapper to get the correct backend. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: hardware TLB state is managed by included backend. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/book3s/tlbflush.h>, #include <asm/nohash/tlbflush.h>. Integrated with Book3S, BookE/nohash, MMU invalidation, and generic MM.

Risks: configuration must include exactly the backend matching the built MMU family. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 11 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h

Purpose: Declares kernel transactional-memory save, reclaim, and restore hooks.

Important APIs/types/functions: `tm_reclaim()`, `tm_reclaim_current()`, `tm_recheckpoint()`, `tm_save_sprs()`, `tm_restore_sprs()`, and `tm_suspend_disabled`. Source-visible declarations include: extern void tm_reclaim(struct thread_struct *thread,; extern void tm_reclaim_current(uint8_t cause);; extern void tm_recheckpoint(struct thread_struct *thread);; extern void tm_save_sprs(struct thread_struct *thread);; extern void tm_restore_sprs(struct thread_struct *thread);; extern bool tm_suspend_disabled;.

Control flow: context switch, signal, ptrace, and exception code reclaim or recheckpoint transactional state around user/kernel transitions. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: transactional checkpointed registers persist in `thread_struct` and hardware TM SPRs. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/tm.h>. Integrated with POWER transactional memory, signal handling, context switch, ptrace, and suspend/CPU feature code.

Risks: ordering mistakes can expose checkpointed state or corrupt transactions during signals and context switches. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 22 lines, 626 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h

Purpose: Declares PowerPC NUMA, CPU, cache, and PCI topology helpers.

Important APIs/types/functions: node/cpu masks, `pcibus_to_node()`, `node_distance()`, associativity update hooks, sibling/core/cache masks, SMT controls, and topology update declarations. Source-visible declarations include: #define _ASM_POWERPC_TOPOLOGY_H; struct device;; struct device_node;; struct drmem_lmb;; #define RECLAIM_DISTANCE 10; #define cpumask_of_node(node) ((node) == -1 ? \; struct pci_bus;; extern int pcibus_to_node(struct pci_bus *bus);.

Control flow: firmware/OF topology is parsed into node and CPU masks used by scheduler, memory allocator, and PCI placement. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: NUMA node, CPU mask, and distance data persist globally and per CPU. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/mmzone.h>, #include <asm-generic/topology.h>, #include <asm/cputable.h>, #include <asm/smp.h>, #include <linux/cpu_smt.h>, #include <linux/cpumask.h>, #include <asm/cputhreads.h>. Integrated with scheduler domains, NUMA memory policy, PCI locality, CPU hotplug, and device-tree associativity.

Risks: bad topology maps degrade scheduling and can allocate memory on the wrong NUMA node. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 181 lines, 4449 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h

Purpose: Defines PowerPC tracepoints for hypervisor, OPAL, RTAS, interrupt, and exception events.

Important APIs/types/functions: `TRACE_EVENT` definitions, hcall/opal tracepoint registration hooks, RTAS event structures, and trace include metadata. Source-visible declarations include: #define TRACE_SYSTEM powerpc; #define _TRACE_POWERPC_H; struct pt_regs;; extern int hcall_tracepoint_regfunc(void);; extern void hcall_tracepoint_unregfunc(void);; extern int opal_tracepoint_regfunc(void);; extern void opal_tracepoint_unregfunc(void);; #define TRACE_INCLUDE_PATH asm.

Control flow: tracepoint users register probes and instrumentation records arguments when firmware or exception paths call tracepoints. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: tracepoint enable state is managed by tracing core; event payloads are transient. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/tracepoint.h>, #include <asm/rtas-types.h>, #include <trace/define_trace.h>. Integrated with ftrace/perf, hypervisor calls, OPAL, RTAS, interrupt, and exception diagnostics.

Risks: tracepoint argument layouts become tooling ABI and must not add heavy work to hot paths. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 347 lines, 7436 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h

Purpose: Registers the PowerPC timebase trace clock.

Important APIs/types/functions: `trace_clock_ppc_tb()` and `ARCH_TRACE_CLOCKS` entry. Source-visible declarations include: #define _ASM_PPC_TRACE_CLOCK_H; extern u64 notrace trace_clock_ppc_tb(void);; #define ARCH_TRACE_CLOCKS { trace_clock_ppc_tb, "ppc-tb", 0 },.

Control flow: tracing can select a raw timebase-backed clock for event timestamps. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: clock state is hardware timebase plus tracing selection. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/types.h>. Integrated with ftrace/perf timestamping and PowerPC timebase.

Risks: timestamp interpretation depends on stable timebase frequency and notrace recursion safety. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 17 lines, 372 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/trace_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108.h

Purpose: Defines Tundra TSI108 host bridge register windows, offsets, and platform hooks.

Important APIs/types/functions: region size/offset constants, Ethernet/MPIC/UART/I2C/DMA windows, global `tsi108_csr_vir_base`, and PCI bridge helpers. Source-visible declarations include: #define __PPC_KERNEL_TSI108_H; #define TSI108_REG_SIZE (0x10000); #define TSI108_HLP_SIZE 0x1000; #define TSI108_PCI_SIZE 0x1000; #define TSI108_CLK_SIZE 0x1000; #define TSI108_PB_SIZE 0x1000; #define TSI108_SD_SIZE 0x1000; #define TSI108_DMA_SIZE 0x1000.

Control flow: platform setup maps the CSR region and drivers add offsets to access device blocks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: mapped CSR base persists globally after early ioremap. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/pci-bridge.h>. Integrated with TSI108 board support, PCI host bridge, MPIC, Ethernet, I2C, DMA, UART, and clock blocks.

Risks: offset constants are hardware ABI; a bad base or size points drivers at the wrong register window. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 113 lines, 3264 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h

Purpose: Defines TSI108 interrupt vector numbers, priorities, and register offsets.

Important APIs/types/functions: IRQ source constants, vector count, priority defaults, spurious vector, and interrupt-control register definitions. Source-visible declarations include: #define _ASM_POWERPC_TSI108_IRQ_H; #define TSI108_IRQ_REG_BASE 0; #define TSI108_IRQ(x) (TSI108_IRQ_REG_BASE + (x)); #define TSI108_MAX_VECTORS (36 + 4) /* 36 sources + PCI INT demux */; #define MAX_TASK_PRIO 0xF; #define TSI108_IRQ_SPURIOUS (TSI108_MAX_VECTORS); #define DEFAULT_PRIO_LVL 10 /* initial priority level */; #define IRQ_TSI108_EXT_INT0 TSI108_IRQ(0) /* External Source at INT[0] */.

Control flow: interrupt controller code maps hardware sources to Linux IRQs and programs priority/mask registers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: hardware interrupt mask/priority state persists in TSI108 registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with TSI108 MPIC/interrupt setup and board device IRQ routing.

Risks: vector numbering must match hardware and PCI INT demux sources or devices receive wrong IRQs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 110 lines, 3916 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h

Purpose: Defines TSI108 PCI inbound/outbound translation register offsets.

Important APIs/types/functions: P2O BAR/page-size registers and PFAB IO/MEM/PFM register offsets. Source-visible declarations include: #define _ASM_POWERPC_TSI108_PCI_H; #define TSI108_PCI_P2O_BAR0 (TSI108_PCI_OFFSET + 0x10); #define TSI108_PCI_P2O_BAR0_UPPER (TSI108_PCI_OFFSET + 0x14); #define TSI108_PCI_P2O_BAR2 (TSI108_PCI_OFFSET + 0x18); #define TSI108_PCI_P2O_BAR2_UPPER (TSI108_PCI_OFFSET + 0x1c); #define TSI108_PCI_P2O_PAGE_SIZES (TSI108_PCI_OFFSET + 0x4c); #define TSI108_PCI_PFAB_BAR0 (TSI108_PCI_OFFSET + 0x204); #define TSI108_PCI_PFAB_BAR0_UPPER (TSI108_PCI_OFFSET + 0x208).

Control flow: PCI host bridge setup programs address windows for CPU-to-PCI and PCI-to-memory access. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: PCI translation windows persist in bridge registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/tsi108.h>. Integrated with TSI108 PCI host bridge setup, DMA, and resource assignment.

Risks: incorrect window programming can expose memory or make PCI config/DMA unreachable. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 1191 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h

Purpose: Extends PowerPC UAPI types with kernel vector type support.

Important APIs/types/functions: `uapi/asm/types.h` include and optional `vector128` typedef under Altivec-enabled compiler builds. Source-visible declarations include: #define _ASM_POWERPC_TYPES_H; typedef __vector128 vector128;.

Control flow: kernel code needing a 128-bit vector scalar includes this arch type wrapper. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/types.h>. Integrated with Altivec/VSX code, ptrace/vector save areas, and generic type includes.

Risks: compiler feature guards must match available vector extensions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 20 lines, 575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h

Purpose: Implements PowerPC user-memory access, copy, clear, and nofault primitives.

Important APIs/types/functions: `get_user/put_user`, unchecked forms, exception-table assembly, KUAP allow/prevent windows, raw copy helpers, `copy_{to,from}_user`, string helpers, and VMX copy threshold. Source-visible declarations include: #define _ARCH_POWERPC_UACCESS_H; #define TASK_SIZE_MAX TASK_SIZE_USER64; #define VMX_COPY_THRESHOLD 3328; #define __put_user(x, ptr) \; #define put_user(x, ptr) \; #define __put_user_asm_goto(x, addr, label, op) \; #define __put_user_asm_goto(x, addr, label, op) \; #define __put_user_asm2_goto(x, ptr, label) \.

Control flow: callers validate or rely on prevalidated user ranges, temporarily allow user access, perform asm loads/stores/copies, and fix up faults through exception tables. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is task address space, KUAP access state, and destination buffers; no persistent header-owned state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sizes.h>, #include <asm/processor.h>, #include <asm/page.h>, #include <asm/extable.h>, #include <asm/kup.h>, #include <asm/asm-compat.h>, #include <asm-generic/access_ok.h>. Integrated with syscalls, filesystems, networking, signal handling, BPF, ptrace, and generic usercopy hardening.

Risks: exception fixups, access_ok/KUAP ordering, 32/64-bit constraints, and partial-copy semantics are security-critical. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 599 lines, 17598 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h

Purpose: Declares the early debug console function-pointer interface.

Important APIs/types/functions: `udbg_putc`, `udbg_flush`, `udbg_getc`, `udbg_getc_poll`, early init helpers, and simple put/get wrappers. Source-visible declarations include: #define _ASM_POWERPC_UDBG_H; extern void (*udbg_putc)(char c);; extern void (*udbg_flush)(void);; extern int (*udbg_getc)(void);; extern int (*udbg_getc_poll)(void);; struct device_node;.

Control flow: early platform code installs backend callbacks and printk/debug paths emit characters before full console registration. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global function pointers persist until replaced or unused after console handoff. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/init.h>. Integrated with early boot console, xmon, firmware consoles, serial/RTAS/OPAL debug backends.

Risks: callbacks may run very early or in crash paths, so they must avoid sleeping and invalid mappings. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 56 lines, 1736 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h

Purpose: Declares IBM 4xx Universal Interrupt Controller setup hooks.

Important APIs/types/functions: `uic_init_tree()` and `uic_get_irq()`. Source-visible declarations include: #define _ASM_POWERPC_UIC_H; extern void __init uic_init_tree(void);; extern unsigned int uic_get_irq(void);.

Control flow: platform IRQ initialization builds the UIC tree and runtime interrupt entry asks it for the pending IRQ. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: UIC mask/status hardware state is owned by the implementation. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC 4xx interrupt controller and device-tree IRQ setup.

Risks: tree setup must match cascaded UIC topology or interrupt dispatch loses lines. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 17 lines, 403 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h

Purpose: Defines PowerPC Ultravisor return codes and call numbers.

Important APIs/types/functions: UV return-code aliases to hypervisor codes and call IDs such as write PATE, share/unshare page, page-in/out, mem-slot registration, invalidation, and SVM terminate. Source-visible declarations include: #define _ASM_POWERPC_ULTRAVISOR_API_H; #define U_BUSY H_BUSY; #define U_FUNCTION H_FUNCTION; #define U_NOT_AVAILABLE H_NOT_AVAILABLE; #define U_P2 H_P2; #define U_P3 H_P3; #define U_P4 H_P4; #define U_P5 H_P5.

Control flow: ultravisor wrappers pass these call IDs to low-level UV call assembly. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state resides in ultravisor-managed secure memory and partition tables. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/hvcall.h>. Integrated with secure VM, protected KVM, ultravisor firmware, and page sharing/migration code.

Risks: call numbers and return code meanings are firmware ABI and must match the ultravisor specification. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 39 lines, 941 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h

Purpose: Defines Apple UniNorth/U3/U4 bridge, AGP/GART, clock, power, and HyperTransport register constants.

Important APIs/types/functions: config-space offsets, GART control bits, AGP status/control fields, clock stop/reset bits, address select masks, and HT bridge registers. Source-visible declarations include: #define __ASM_UNINORTH_H__; #define UNI_N_ADDR_SELECT 0x48; #define UNI_N_ADDR_COARSE_MASK 0xffff0000 /* 256Mb regions at *0000000 */; #define UNI_N_ADDR_FINE_MASK 0x0000ffff /* 16Mb regions at f*000000 */; #define UNI_N_CFG_GART_BASE 0x8c; #define UNI_N_CFG_AGP_BASE 0x90; #define UNI_N_CFG_GART_CTRL 0x94; #define UNI_N_CFG_INTERNAL_STATUS 0x98.

Control flow: PowerMac platform and AGP/IOMMU code programs bridge registers using these masks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: bridge register settings persist in host bridge hardware. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerMac PCI/AGP, UniNorth IOMMU/GART, clock/power management, and platform setup.

Risks: register bits are chipset-specific; wrong values can break PCI/AGP DMA or platform power state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 230 lines, 8409 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h

Purpose: Wraps PowerPC syscall-number UAPI and declares generic syscall implementation wants.

Important APIs/types/functions: `NR_syscalls`, many `__ARCH_WANT_*` feature macros, and 32-bit syscall entry declarations. Source-visible declarations include: #define _ASM_POWERPC_UNISTD_H_; #define NR_syscalls __NR_syscalls; #define __ARCH_WANT_NEW_STAT; #define __ARCH_WANT_OLD_READDIR; #define __ARCH_WANT_STAT64; #define __ARCH_WANT_SYS_ALARM; #define __ARCH_WANT_SYS_GETHOSTNAME; #define __ARCH_WANT_SYS_IPC.

Control flow: generic syscall code uses the want macros to include legacy implementations and syscall tables use `NR_syscalls`. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: syscall ABI is generated and immutable for the running kernel. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/unistd.h>, #include <linux/types.h>, #include <linux/compiler.h>, #include <linux/linkage.h>. Integrated with syscall tables, compat syscalls, generic syscall selection, and userspace ABI headers.

Risks: want macro changes can remove legacy syscalls still required by PowerPC ABI. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 56 lines, 1485 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h

Purpose: Includes the generated 32-bit PowerPC syscall-number table.

Important APIs/types/functions: `asm/unistd_32.h` include. Source-visible declarations include: #define _ASM_POWERPC_UNISTD32_H_.

Control flow: compat and 32-bit builds include this wrapper for syscall numbers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state; generated numbers define ABI. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/unistd_32.h>. Integrated with 32-bit syscall tables and UAPI export.

Risks: must track generated syscall list exactly. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 7 lines, 181 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h

Purpose: Defines PowerPC uprobes instruction slots and per-probe arch state.

Important APIs/types/functions: `uprobe_opcode_t`, XOL slot sizes, breakpoint instruction constants, `struct arch_uprobe`, and `struct arch_uprobe_task`. Source-visible declarations include: #define _ASM_UPROBES_H; typedef u32 uprobe_opcode_t;; #define MAX_UINSN_BYTES 8; #define UPROBE_XOL_SLOT_BYTES (MAX_UINSN_BYTES); #define UPROBE_SWBP_INSN BREAKPOINT_INSTRUCTION; #define UPROBE_SWBP_INSN_SIZE 4 /* swbp insn size in bytes */; struct arch_uprobe {; union {.

Control flow: uprobes copies/analyzes the original instruction, plants a breakpoint, and executes an out-of-line slot for probed user instructions. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: per-probe decoded instruction state and per-task saved state persist while probes are armed. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/notifier.h>, #include <asm/probes.h>. Integrated with uprobes, instruction decoder, notifier chain, and breakpoint exception handling.

Risks: instruction length/prefix handling and single-step emulation must be correct or probed tasks misexecute. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 35 lines, 770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h

Purpose: Defines the legacy PowerPC `struct user` core-dump/ptrace layout.

Important APIs/types/functions: `struct user` with pt_regs, u-area sizing, start addresses, signal, and register offset fields. Source-visible declarations include: #define _ASM_POWERPC_USER_H; struct user {; struct user_pt_regs regs; /* entire machine state */.

Control flow: old ptrace and core dump tooling can interpret saved task register and memory metadata through this layout. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serialized process state persists in core files or ptrace-visible structures. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <asm/page.h>. Integrated with ptrace, core dumps, debuggers, and legacy user ABI.

Risks: field layout is external ABI and tied to `asm/ptrace.h` register structures. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 47 lines, 1997 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h

Purpose: Declares the Virtual Accelerator Switchboard window and coprocessor request interface.

Important APIs/types/functions: VAS FIFO/threshold constants, window status flags, `struct vas_window`, `struct vas_tx_win_attr`, `struct coprocessor_request_block`, field helper macros, open/close/paste/IRQ APIs. Source-visible declarations include: #define _ASM_POWERPC_VAS_H; #define VAS_RX_FIFO_SIZE_MIN (1 << 10) /* 1KB */; #define VAS_RX_FIFO_SIZE_MAX (8 << 20) /* 8MB */; #define VAS_THRESH_DISABLED 0; #define VAS_THRESH_FIFO_GT_HALF_FULL 1; #define VAS_THRESH_FIFO_GT_QTR_FULL 2; #define VAS_THRESH_FIFO_GT_EIGHTH_FULL 3; #define VAS_WIN_ACTIVE 0x0 /* Used in platform independent */.

Control flow: drivers open RX/TX windows, configure FIFO/credit/interrupt attributes, paste CRBs to submit work, and close or migrate windows. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: window objects, FIFO mappings, credits, IRQs, and attached mm/context state persist while devices use VAS. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sched/mm.h>, #include <linux/mmu_context.h>, #include <asm/icswx.h>, #include <uapi/asm/vas-api.h>. Integrated with NX/GZIP/crypto acceleration, user VAS API, hypervisor hcalls, IRQs, and mm context handling.

Risks: credit accounting, window migration, and user-mapped paste addresses are concurrency and security sensitive. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 294 lines, 8100 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h

Purpose: Defines PowerPC vDSO layout constants, symbol-offset helpers, and assembly symbol macros.

Important APIs/types/functions: `VDSO_VERSION_STRING`, page count, `VDSO64_SYMBOL`, `VDSO32_SYMBOL`, and local/global vDSO function symbol macros. Source-visible declarations include: #define _ASM_POWERPC_VDSO_H; #define VDSO_VERSION_STRING LINUX_2.6.15; #define __VDSO_PAGES 4; #define VDSO64_SYMBOL(base, name) ((unsigned long)(base) + (vdso64_offset_##name)); #define VDSO32_SYMBOL(base, name) ((unsigned long)(base) + (vdso32_offset_##name)); #define V_FUNCTION_BEGIN(name) \; #define V_FUNCTION_END(name) \; #define V_LOCAL_FUNC(name) (name).

Control flow: kernel maps vDSO pages and resolves exported helper addresses from generated offsets. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: vDSO image pages and symbol offsets persist as user-mapped ABI. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <generated/vdso64-offsets.h>, #include <generated/vdso32-offsets.h>. Integrated with time/getcpu/getrandom vDSO, signal trampolines, generated offsets, and userspace libc.

Risks: page count and symbol names are ABI-sensitive and must match generated vDSO offset headers. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 54 lines, 1049 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h

Purpose: Defines PowerPC architecture-specific data embedded in the generic vDSO data page.

Important APIs/types/functions: `SYSCALL_MAP_SIZE` and `struct vdso_arch_data` variants for 32-bit and 64-bit builds. Source-visible declarations include: #define _ASM_POWERPC_VDSO_ARCH_DATA_H; #define SYSCALL_MAP_SIZE ((NR_syscalls + 31) / 32); struct vdso_arch_data {; struct vdso_arch_data {.

Control flow: kernel populates syscall maps or architecture data that vDSO helpers read without syscalls. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: mapped vDSO data persists read-only or read-mostly for userspace. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/unistd.h>, #include <linux/types.h>. Integrated with generic vDSO data, syscall availability mapping, and libc vDSO consumers.

Risks: structure layout must stay synchronized with vDSO code compiled for user mapping. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 37 lines, 1171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h

Purpose: Selects the PowerPC vDSO architecture clock mode.

Important APIs/types/functions: `VDSO_ARCH_CLOCKMODES` set to `VDSO_CLOCKMODE_ARCHTIMER`. Source-visible declarations include: #define _ASM_POWERPC_VDSO_CLOCKSOURCE_H; #define VDSO_ARCH_CLOCKMODES VDSO_CLOCKMODE_ARCHTIMER.

Control flow: generic vDSO time code uses this macro to decide supported fast clocksource modes. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: clocksource selection persists in vDSO data/config. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with generic vDSO timekeeping and PowerPC timebase clocksource.

Risks: the selected mode must match the implementation used by PowerPC vDSO timebase reads. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 7 lines, 182 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/getrandom.h

Purpose: Implements PowerPC arch helpers for vDSO getrandom data access.

Important APIs/types/functions: `__arch_get_vdso_u_rng_data()` and architecture binding macro for vDSO RNG data. Source-visible declarations include: #define _ASM_POWERPC_VDSO_GETRANDOM_H; struct vdso_rng_data *data;; #define __arch_get_vdso_u_rng_data __arch_get_vdso_u_rng_data.

Control flow: vDSO getrandom code locates the RNG data area relative to the vDSO data page and uses it for fast random generation when valid. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: RNG data is kernel-populated vDSO state mapped into userspace. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/vdso_datapage.h>. Integrated with generic vDSO getrandom, PowerPC vDSO data page, and userspace libc wrappers.

Risks: offset calculations must match vDSO data layout or userspace reads invalid RNG metadata. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 67 lines, 1889 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/getrandom.h -->
