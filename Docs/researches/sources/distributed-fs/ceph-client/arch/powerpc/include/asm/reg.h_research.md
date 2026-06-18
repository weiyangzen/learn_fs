# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg.h

Purpose: This is the main PowerPC register definition header, covering common MSR bits, SPR numbers, fault/status bitfields, power/performance/debug/cache controls, PVR values, SPRG usage conventions, and inline helpers for MSR/SPR access.

Important APIs/types/functions: It defines MSR bit numbers and masks, transactional memory state helpers, default kernel/user MSR values by Book3S/BookE/32/64-bit config, FPSCR/SPEFSCR fields, SPR numbers for PID, CTR, DSCR, DABR/DAWR, DAR/DSISR, time base, hypervisor registers, FSCR/HFSCR, LPCR, PCR, HID, BAT, cache, performance monitor, EBB, SIER/SIAR/SDAR, and many processor-specific registers. It documents SPRG usage and defines `GET_PACA`, `SET_PACA`, `GET_SCRATCH0`, `SET_SCRATCH0`, `MTFSF_L`, PVR extraction macros, `ppc_inst_t`, `mfmsr`, `mtmsr`, `mtmsr_isync`, `mfspr`, `mtspr`, `wrtspr`, `wrtee`, MSR strict-control helpers, 32-bit segment register helpers, `current_stack_frame`, `current_stack_pointer`, SCOM accessors, and `ppc_save_regs`.

Control flow: Most content is compile-time register encoding. Inline functions and macros emit direct MSR/SPR operations with required barriers or feature-conditioned `isync`. Assembly macros select PACA/scratch SPRs based on Book3S HV mode and other config.

State and persistence: The header describes core CPU state: MSR, SPRs, perf counters, fault registers, power management registers, debug registers, SPRGs, PVRs, and stack pointer. Inline helpers mutate processor state directly and persist until overwritten by context switch, exception handling, or platform code.

Dependencies and integration points: It includes cputable, asm constants, feature fixups, BookE/FSL/8xx variant headers, and stringification. It is foundational for exception code, MMU, PMU, KVM, idle/power management, debugging, ptrace, cache/TLB control, boot CPU detection, and assembly code.

Risks and test signals: Numeric definitions are architectural contracts. Wrong masks can mis-handle faults, privilege, endian, TM, radix/hash, or hypervisor state. Inline SPR/MSR helpers are privileged and ordering-sensitive. Tests include broad PowerPC build matrix, boot tests on Book3S/BookE/8xx/FSL configs, PMU/perf tests, fault injection for DSISR/SRR1 decoding, KVM HV tests, idle/power tests, PVR matching, and objdump validation of MSR/SPR instructions.
