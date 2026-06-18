# sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/sysreg.h` Central arm64 system-register dictionary and access layer, including encodings, PSTATE helpers, cache/TLBI/AT instruction IDs, debug/trace/GIC/timer/perf registers, SCTLR/MAIR/feature bits, PIE/POE/GCS encodings, and read/write helper macros for named and encoded registers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
sys_reg()/sys_insn(), sys_reg_* extractors, __emit_inst(), SET_PSTATE_* and set_pstate_*(), many SYS_* and OP_* register/instruction encodings, INIT_SCTLR_EL1/EL2 values, MAIR_ATTR*, ID_AA64MMFR0 granule/PARANGE helpers, CPACR/GCR/RGSR/TFSR/GIC/PIE/POE/GCS fields, gicr_insn/gic_insn, mrs_s/msr_s, read_sysreg(), write_sysreg(), read_sysreg_s(), write_sysreg_s(), sysreg_clear_set*(), write_sysreg_hcr(), read_sysreg_par(), SYS_FIELD_* helpers. The file is 1271 lines / 49261 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Most control flow is macro expansion into inline assembly. Encoded-register helpers synthesize mrs/msr instructions for old binutils; HCR writes conditionally insert DSB/ISB for Ampere erratum; PAR reads optionally fence around reads for ARM64_WORKAROUND_1508412.

### State, Persistence, And Dependencies
No high-level storage. Side effects are direct CPU system-register writes, instruction execution, and alternative-patched instruction sequences. Depends on bits, stringify, kasan-tags, kconfig, gpr-num, generated sysreg-defs.h, alternative, bitfield, build_bug, types; every low-level arm64 subsystem consumes it: MMU, cache/TLB, KVM, perf, debug, timers, GIC, PAC, MTE, SME/SVE, GCS, CCA, and exception entry.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Numeric encodings are architecture ABI; a wrong field can write the wrong system register. Inline asm constraints and old-binutils fallbacks must be exact. Erratum fences and alternative patching are correctness and security critical.

### Test Signals
Cross-build with old/new binutils, objdump generated mrs/msr/tlbi/at instructions, boot diverse CPUs, run KVM/perf/timer/GIC/MTE/PAC/GCS tests, and validate generated sysreg-defs synchronization.
