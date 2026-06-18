<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h

Purpose: Provides vDSO-safe processor relaxation and hardware multithreading priority helpers for PowerPC.

Important APIs/types/functions: `HMT_very_low()` through `HMT_high()` priority nops on PPC64 and `cpu_relax()` with feature patching for pre-POWER10 versus POWER10 `wait 2,0` pause behavior.

Control flow: Spin loops call `cpu_relax()`, which either emits low/medium priority nops or a patched short wait depending on `CPU_FTR_ARCH_31`; non-PPC64 builds degrade to a compiler barrier.

State and persistence: No persistent state is stored. The only state effect is transient thread priority/pause behavior on SMT hardware.

Dependencies and integration points: Includes CPU feature and feature-fixup headers; integrated by vDSO and low-level polling code that cannot rely on full kernel facilities.

Risks: Instruction choice is CPU-generation-sensitive. Incorrect feature patching can hurt spin performance or use unsupported wait instructions in user-visible vDSO code.

Test signals: PPC64 and PPC32 compile coverage, objdump of patched alternatives, and spin-loop latency/scheduler smoke tests on POWER9 and POWER10 class machines.

Source read size: 41 lines, 1258 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/processor.h -->
