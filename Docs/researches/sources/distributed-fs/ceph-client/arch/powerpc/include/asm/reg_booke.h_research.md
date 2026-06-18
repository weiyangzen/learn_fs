# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_booke.h

Purpose: This header defines BookE-specific MSR bits, SPR numbers, exception/debug/MMU/cache/timer fields, thread-management registers, and access helpers for BookE PowerPC variants.

Important APIs/types/functions: It defines BookE MSR fields (`MSR_GS`, `MSR_UCLE`, `MSR_SPE`, `MSR_IS`, `MSR_DS`, `MSR_CM`), BookE kernel/user MSR defaults, many SPRs for DECAR/IVPR/USPRG/SPRG/EPCR/MSRP/IAC/DAC/DVC/LPID/MAS/TLB/guest registers/IVOR/MCSR/DBSR/DBCR/TCR/TSR/cache/EPCR/EPLC/EPSC/thread control, machine-check bits for 47x/e500, debug event masks, watchdog/FIT/PIT fields, L1/L2 cache controls, branch unit controls, guest/hypervisor routing fields, and inline `mftmr`/`mttmr`. It declares `global_dbcr0`.

Control flow: BookE exception setup uses IVPR/IVOR and MSR defaults, MMU code uses MAS/TLB/EPLC/EPSC fields, debug and ptrace code uses DBCR/DBSR/IAC/DAC definitions, timer/watchdog code uses TCR/TSR, cache code uses L1/L2/BUCSR fields, and threaded core code uses TMR/TENS registers.

State and persistence: The header maps persistent BookE CPU state in SPRs: MMU assist registers, debug control/status, machine-check syndrome, timer/watchdog state, cache controls, guest/hypervisor context, and thread enable state. `global_dbcr0` suggests global debug-control shadowing in implementation code.

Dependencies and integration points: It includes opcode macros for TMR instructions and is included from `reg.h` when `CONFIG_BOOKE` is enabled. It integrates with BookE exception vectors, KVM/guest state, e500/47x hardware, debug/hw-breakpoint support, PMU/timer code, and cache/TLB management.

Risks and test signals: BookE has many overlapping and implementation-specific SPR numbers, so config guards are critical. Debug range/mask fields can alter ptrace breakpoints. Watchdog reset fields can reset core/chip/system. Tests include BookE/e500/47x build and boot, TLB miss/refill, machine-check decoding, watchdog/FIT/PIT behavior, hardware breakpoints, KVM BookE guest paths, and cache/branch predictor setup.
