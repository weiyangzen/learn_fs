<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h

**Purpose:** Provides MIPS arch-optimized bit-reversal helpers.

**Important APIs/types/functions:** `__arch_bitrev32`, `__arch_bitrev16`, and `__arch_bitrev8` use the `bitswap` instruction combined with byte swaps for 16/32-bit widths.

**Control flow:** Header-only inline assembly returns reversed bit order.

**State, dependencies, integration:** Used by generic bitrev APIs when architecture support is enabled.

**Risks and test signals:** Requires CPU/toolchain support for `bitswap`. Test known bit patterns for all widths and build on CPUs/configs that select this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h -->
