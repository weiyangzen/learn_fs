<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h

**Purpose:** Supplies assembly string and assembler macros for kernel versus user memory/cache accesses, selecting EVA instructions when configured.

**Important APIs/types/functions:** Defines `kernel_*` operations for cache, pref, ll/sc, loads, and stores; `user_*` variants become EVA instructions such as `lwe`, `swe`, `cachee`, and `prefe` under `CONFIG_EVA`, or kernel equivalents otherwise.

**Control flow:** Preprocessor emits either C inline-asm strings or assembler macros depending on `__ASSEMBLER__`, and adapts doubleword operations for 32-bit builds.

**State, dependencies, integration:** Used by low-level user access, cache, atomic, and assembly code paths that must work in Enhanced Virtual Addressing mode.

**Risks and test signals:** Wrong user/kernel opcode selection can fault or access the wrong address space. Test EVA and non-EVA builds, 32/64-bit doubleword fallbacks, and assembler/C macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h -->
