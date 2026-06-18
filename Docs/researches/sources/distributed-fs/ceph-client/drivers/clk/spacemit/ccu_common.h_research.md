# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h

Purpose: defines the common data layout and helper macros shared by SpacemiT CCU clock implementations and SoC tables.

Important APIs and control flow: `struct ccu_common` embeds the CCF `clk_hw`, the main and lock regmaps, and a union of register fields used by DDN/MIX (`reg_ctrl`, `reg_fc`, `mask_fc`) or PLL (`reg_swcr1`, `reg_swcr2`, `reg_swcr3`) clocks. `hw_to_ccu_common()` recovers the container from `clk_hw`. `struct spacemit_ccu_data` carries optional `reset_name`, `hws`, and `num` match data. `ccu_read()` and `ccu_update()` wrap regmap read/update against the named register members, and `spacemit_ccu_probe()` is declared for SoC drivers.

State and persistence behavior: the header owns no runtime state but fixes the in-memory ABI between all SpacemiT clock descriptors and `ccu_common.c`. The union means each clock type must initialize only the register fields its operations use. The `clk_hw` must remain embedded after the register fields so `container_of()` conversions match the macros in PLL/MIX/DDN headers.

Dependencies and integration points: depends on Linux CCF, platform-device declarations, regmap, and local clock type headers using the same embedding convention. SoC files use `struct spacemit_ccu_data` in OF match tables, and operation files rely on `ccu_read()`/`ccu_update()` to hide regmap details.

Risks and test signals: risks include silent register-field aliasing through the union, unchecked `regmap_read()` return values inside `ccu_read()`, macro arguments needing to match exact member suffixes, and all custom clock types needing `struct ccu_common` placement compatible with `hw_to_ccu_common()`. Test signals are clean compile across PLL/MIX/DDN users, successful container conversions under runtime clock ops, correct register offsets reached by each op type, and graceful behavior when regmap operations fail or return stale values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h -->
