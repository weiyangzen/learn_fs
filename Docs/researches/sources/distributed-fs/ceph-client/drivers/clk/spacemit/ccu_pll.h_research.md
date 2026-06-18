# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h

Purpose: declares SpacemiT PLL data structures and macros for regular PLL and PLLA clock descriptors.

Important APIs and control flow: `struct ccu_pll_rate_tbl` maps a rate to SWCR register values; `CCU_PLL_RATE()` and `CCU_PLLA_RATE()` initialize regular or type-A entries. `struct ccu_pll_config` stores a rate table and lock-register metadata, while `struct ccu_pll` embeds `ccu_common`. `CCU_PLL_COMMON_HWINIT()` creates a single-parent CCF initializer using firmware parent index 0. `CCU_PLL_DEFINE()` and `CCU_PLLA_DEFINE()` emit static PLL objects using the exported regular or PLLA operation tables.

State and persistence behavior: the header emits static descriptors; rate state persists in PLL control registers. Regular PLLs use SWCR3 bit 31 as enable and SWCR1/SWCR3 as config, while PLLA uses SWCR2 bit 16 as enable and SWCR1/SWCR2/SWCR3 as config.

Dependencies and integration points: depends on CCF, `ccu_common.h`, and exported operation tables from `ccu_pll.c`. SoC files place generated objects into clock-provider arrays and rely on common probe to fill regmap pointers and PLL lock regmap.

Risks and test signals: risks include parent index 0 requiring the DT clock parent order to be correct, table entries needing exact hardware register encodings, lock masks needing to match the SoC POSR bits, and macro-created descriptors not checking table size. Test signals include compile-time coverage for regular and PLLA users, correct parent resolution from DT, PLL lock bit association, and table-driven rate reads/writes matching hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h -->
