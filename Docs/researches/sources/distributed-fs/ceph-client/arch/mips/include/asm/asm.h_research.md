<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h

**Purpose:** Defines common MIPS assembler macros for function declarations, CFI, pointer/register-size abstraction, panic/print helpers, CP0 access names, LL/SC branch workaround, and cache barriers.

**Important APIs/types/functions:** `LEAF`, `NESTED`, `END`, `EXPORT`, `FEXPORT`, `ASM_PANIC`, `ASM_PRINT`, `REG_*`, `INT_*`, `LONG_*`, `PTR_*`, `MFC0`, `MTC0`, `SC_BEQZ`, and `R10KCBARRIER`.

**Control flow:** Compile-time macros select ABI32/N32/ABI64 instruction forms and MIPS ISA capabilities.

**State, dependencies, integration:** Included by nearly all MIPS assembly and some inline asm code. It depends on sgidefs, EVA, and ISA revision definitions.

**Risks and test signals:** A macro bug affects many low-level paths, including stack frames, unwinding, and atomics. Test 32-bit, n32, and 64-bit assembly builds, microMIPS/VDSO CFI behavior, and R10000 LL/SC workaround codegen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h -->
