<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h

Purpose: names LoongArch general-purpose registers for assembly sources using ABI-friendly aliases.
Important APIs and types: maps `$r0` through `$r31` to aliases such as `zero`, `ra`, `tp`, `sp`, argument registers, temporaries, saved registers, and `u0`/`fp` according to LoongArch conventions.
Control flow: no runtime flow; assembly files include it so entry, exception, context-switch, and FPU code can use stable symbolic names.
State and persistence: no stored state, but the names define how assembly preserves and interprets calling-convention registers.
Dependencies and integration: used heavily by `entry.S`, `head.S`, `genex.S`, `fpu.S`, `stackframe.h`, and other low-level assembly.
Risks and test signals: a wrong alias corrupts calling convention globally. Signals are assembler build success, boot, syscall entry, context switch, and exception tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/regdef.h -->
