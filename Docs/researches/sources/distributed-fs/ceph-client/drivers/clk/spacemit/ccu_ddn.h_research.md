# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h

Purpose: declares the SpacemiT DDN clock descriptor and macro used by SoC files to define rational divider clocks.

Important APIs and control flow: `struct ccu_ddn` holds embedded `ccu_common`, numerator and denominator masks/shifts, and a `pre_div`. `CCU_DDN_INIT()` builds a one-parent `clk_init_data` from another SpacemiT clock's `common.hw`. `CCU_DDN_DEFINE()` emits a static `struct ccu_ddn` with generated bit masks and operation pointer `spacemit_ccu_ddn_ops`. `hw_to_ccu_ddn()` converts from `clk_hw` through `ccu_common`.

State and persistence behavior: the header creates static clock objects in the including SoC file; runtime rate state is held in hardware registers, not in the descriptor. Generated masks are compile-time constants derived from shift/width arguments.

Dependencies and integration points: depends on bitops, CCF, `ccu_common.h`, and `spacemit_ccu_ddn_ops` from `ccu_ddn.c`. It integrates with SoC tables by exposing each generated object's `common.hw` into a onecell array.

Risks and test signals: risks include invalid shift/width combinations creating wrong `GENMASK()` values, only supporting `CCU_PARENT_HW`-style SpacemiT parents, and all DDN users inheriting the same arithmetic assumptions from `ccu_ddn.c`. Test signals are compile-time generation of expected masks, successful parent resolution for generated clocks, and rate/recalc behavior matching SoC register documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h -->
