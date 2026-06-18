<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h

**Purpose:** Provides architecture hweight/popcount helpers when compiler builtins are usable, otherwise delegates to generic bitops.

**Important APIs/types/functions:** Defines `__arch_hweight8/16/32/64` using `__builtin_popcount`/`__builtin_popcountll` under `ARCH_HAS_USABLE_BUILTIN_POPCOUNT`.

**Control flow:** Compile-time conditional chooses builtin or generic implementation.

**State, dependencies, integration:** Used by Linux bitops hweight APIs.

**Risks and test signals:** Builtin availability must match toolchain codegen support. Test popcount results for all widths and configs with/without builtin support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h -->
