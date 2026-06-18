# sources/distributed-fs/ceph-client/drivers/clk/sprd/common.c

## Purpose
Provides shared Spreadtrum clock registration infrastructure: acquiring a regmap for a clock block, attaching it to all clock descriptors, registering clock hardware, and publishing a device-tree clock provider.

## Important APIs, Types, And Functions
`sprd_clk_regmap_init(struct platform_device *pdev, const struct sprd_clk_desc *desc)` resolves a regmap from `sprd,syscon`, a syscon parent node, or direct MMIO resource. `sprd_clk_probe(struct device *dev, struct clk_hw_onecell_data *clkhw)` registers every non-null `clk_hw` and calls `devm_of_clk_add_hw_provider`. `sprd_clk_set_regmap` assigns the resolved regmap into each `sprd_clk_common`.

## Control Flow
During SoC platform probe, match data supplies a descriptor. Regmap init chooses the access path, initializes MMIO regmap if needed, and stamps the regmap into all common clock records. Probe then iterates the onecell array, skips holes, registers each clock with devm lifetime, and exposes `of_clk_hw_onecell_get` for DT consumers.

## State And Persistence
The persistent runtime state is each clock object's `regmap` pointer plus registered CCF hardware and OF provider records. Hardware register values are not initialized here; individual clock ops mutate them later.

## Dependencies And Integration Points
Depends on regmap, syscon, platform devices, OF address/resource handling, and CCF provider APIs. Every Spreadtrum SoC driver uses this file's exported symbols from its probe function.

## Risks And Edge Cases
The syscon-parent detection uses an `of_get_parent` expression that must always release node references correctly. All descriptor `clk_clks` entries must match the clocks later registered through `hw_clks`; missed entries leave a null regmap and later crashes. Registration stops on first failed clock, leaving devm cleanup to unwind.

## Test Signals
Probe logs should not show syscon/regmap errors or "Couldn't register clock" messages. DT consumers should resolve clocks by phandle. Compile tests should cover syscon and MMIO probe variants.
