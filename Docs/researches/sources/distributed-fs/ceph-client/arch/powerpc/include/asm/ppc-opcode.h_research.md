# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-opcode.h

Purpose: This header is the central PowerPC instruction encoding catalog used by assembly, code patching, emulation, probes, alternatives, and inline assembly that must emit instructions unsupported by older assemblers.

Important APIs/types/functions: It defines register number macros (`__REG_R*`, `_R*`), immediate field helpers (`IMM_L`, `IMM_DS`, `IMM_DQ`, `IMM_HA`, `IMM_H18`), primary opcode and extended opcode constants, instruction images and masks such as `PPC_INST_SYNC`, `PPC_INST_MTMSRD`, and `PPC_INST_BRANCH_COND`, field insertion helpers (`___PPC_RA`, `__PPC_SPR`, `__PPC_SH64`, etc.), and a large set of `PPC_RAW_*` macros that produce 32-bit instruction words. It also provides assembler-string wrappers like `PPC_WAIT`, `PPC_TLBIE_5`, `PPC_COPY`, `LXVD2X`, `XXSWAPD`, `TRECLAIM`, `TABORT`, and `PPC_RAW_TRAP`.

Control flow: There is no runtime control flow in the header. Consumers compose instruction words by ORing base opcodes with encoded operands, then use the raw value in generated code, `.long` inline assembly, patch sites, decode masks, or probe filters. Conditional aliases select 32-bit or 64-bit forms for load/store/cmp macros.

State and persistence: The only state is compile-time constants. Persisted effects occur in generated kernel text when these macros are used for static code, runtime patching, alternatives, or instruction emulation tables.

Dependencies and integration points: It includes `asm/asm-const.h` and is used by assembly helpers, kprobes, feature fixups, barrier code, TLB/cache code, transactional memory paths, radix/hash MMU code, and low-level exception code. It is tightly coupled to ISA encodings and assembler syntax.

Risks and test signals: A single bit error can emit a different privileged instruction, wrong register, wrong page-size invalidation, or broken barrier. Immediate helpers must match sign-extension and alignment rules. Tests include build coverage with old/new binutils, objdump inspection of emitted instructions, kprobes single-step exclusions, runtime TLB/cache/PMU/TM paths on real hardware or emulators, and instruction patch selftests.
