# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-chipid.c

## Purpose

`exynos-chipid.c` identifies Samsung Exynos and Google GS101 SoCs, registers a `soc_device`, and invokes ASV initialization. It supports both syscon-backed ChipID registers and efuse/OTP-style MMIO.

## Important APIs, Types, and Functions

`struct exynos_chipid_variant` describes revision register layout and efuse mode. `soc_ids[]` maps product IDs to names. `exynos_chipid_get_chipid_info()` reads product and revision fields. `exynos_chipid_get_efuse_regmap()` maps resource 0 and builds a clocked MMIO regmap. `exynos_chipid_probe()` performs match-data selection, regmap setup, identity read, soc-bus registration, devm unregister action, and `exynos_asv_init()`.

## Control Flow

Probe obtains variant data from OF. Efuse variants create a local regmap; other variants use `device_node_to_regmap()`. Product/revision are decoded according to variant layout, root DT `model` is copied as machine, `soc_id` is looked up by product ID, `soc_device_register()` is called, then ASV setup is attempted.

## State and Persistence Behavior

The registered soc device persists for the platform-device lifetime and is unregistered by a devm action. ASV may mutate OPP table voltages. No hardware state is changed by identification reads.

## Dependencies and Integration Points

It depends on regmap, syscon, platform resources, soc bus, OF root model, Exynos ChipID register definitions, and `exynos-asv.c`. User space sees soc-bus identity; CPUfreq/thermal may observe ASV voltage changes.

## Risks and Edge Cases

Unknown product IDs fail probe even if raw registers are readable. Root `model` read ignores errors, so machine can be null. The efuse regmap config defines `max_register` using a local `reg_config` initializer expression; build coverage is important. ASV failure fails ChipID probe after soc-device registration, relying on devm action to unwind.

## Test Signals

Test Exynos4210, Exynos850-style, and GS101 variants; unknown product ID; regmap read failures; root model absence; module remove/unbind; ASV supported/unsupported paths; and efuse pclk handling.
