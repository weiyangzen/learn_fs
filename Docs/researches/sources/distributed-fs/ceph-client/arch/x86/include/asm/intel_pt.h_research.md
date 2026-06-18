<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h

## Purpose
Intel Processor Trace helper declarations and MSR/format constants for perf PT integration. The header is 41 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_PT_H`; `#define PT_CPUID_LEAVES 2`; `#define PT_CPUID_REGS_NUM 4 /* number of registers (eax, ebx, ecx, edx) */`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_PT_H`; `#define PT_CPUID_LEAVES 2`; `#define PT_CPUID_REGS_NUM 4 /* number of registers (eax, ebx, ecx, edx) */`; `enum pt_capabilities {`; `void cpu_emergency_stop_pt(void);`; `extern u32 intel_pt_validate_hw_cap(enum pt_capabilities cap);`; `extern u32 intel_pt_validate_cap(u32 *caps, enum pt_capabilities cap);`; `extern int is_intel_pt_event(struct perf_event *event);`; `static inline void cpu_emergency_stop_pt(void) {}`; `static inline u32 intel_pt_validate_hw_cap(enum pt_capabilities cap) { return 0; }`; `static inline u32 intel_pt_validate_cap(u32 *caps, enum pt_capabilities capability) { return 0; }`; `static inline int is_intel_pt_event(struct perf_event *event) { return 0; }`

## Control Flow
Perf PT code configures trace address ranges, output buffers, and MSRs based on these constants and CPU capabilities.

## State and Persistence
State is PT MSR configuration plus perf AUX buffer state managed by Intel PT implementation.

## Dependencies and Integration Points
Depends on perf AUX infrastructure, Intel PMU, CPUID feature detection, MSRs, and virtualization restrictions.

## Risks
Risks include invalid MSR programming, trace packet format drift, and AUX buffer synchronization bugs.

## Test Signals
Tests should run perf intel_pt traces, snapshot/full modes, CPU hotplug, virtualization constraints, and unsupported CPU fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h -->
