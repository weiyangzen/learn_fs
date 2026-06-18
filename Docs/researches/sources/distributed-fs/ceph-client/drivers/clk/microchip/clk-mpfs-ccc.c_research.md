# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-mpfs-ccc.c

Purpose: This file implements the PolarFire SoC Clock Conditioning Circuitry driver. It exposes two fabric CCC PLLs and four divided outputs from each PLL.

Important APIs, types, and functions: Key types are `mpfs_ccc_data`, `mpfs_ccc_pll_hw_clock`, and `mpfs_ccc_out_hw_clock`. Important functions are `mpfs_ccc_pll_recalc_rate`, `mpfs_ccc_pll_get_parent`, `mpfs_ccc_register_outputs`, `mpfs_ccc_register_plls`, and `mpfs_ccc_probe`. It registers a platform driver for compatible `microchip,mpfs-ccc` at `core_initcall`.

Control flow: Probe maps two PLL resources, allocates a onecell clock data block, registers PLL0 and PLL1 using parent firmware names `pll*_ref0` and `pll*_ref1`, then registers four divider outputs for each PLL. The provider is published with `devm_of_clk_add_hw_provider`. PLL recalc reads feedback and reference dividers; parent selection reads `MPFS_CCC_REFCLK_SEL`.

State and persistence behavior: There is no private mutable state after registration except clock wrapper fields. PLL and output divider state is in the CCC MMIO resources. A global spinlock protects output divider writes because outputs share post-divider registers and the hardware has software-locked write behavior.

Dependencies and integration points: It depends on CCF, platform resource mapping, OF clock provider APIs, dt-binding IDs from `microchip,mpfs-clock.h`, and firmware-provided reference clocks. Fabric and peripheral consumers reference CCC output IDs through device tree.

Risks and edge cases: The `hw_data.hws[out_hw->id - 2]` packing assumes only PLL IDs and output IDs are present; the source comment warns DLL additions would need rework. Shared post-divider registers make locking important. Test signals include provider registration with two resources, expected PLL rates for both reference inputs, all eight output IDs resolving, concurrent divider changes, and fabric devices consuming CCC outputs.
