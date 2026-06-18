# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/pinctrl-ti-iodelay.c

## Purpose

This driver programs the Texas Instruments DRA7 IO Delay module through the Linux pinctrl pinconf path. It parses `pinctrl-pin-array` Device Tree entries containing register offsets plus agnostic and gnostic delay values, computes hardware coarse/fine delay fields from bootloader calibration registers, writes per-pin IO delay registers through regmap, and exposes debugfs details when enabled.

## Important APIs, Types, and Functions

Key data types are `struct ti_iodelay_reg_data` for SoC register layout and masks, `struct ti_iodelay_reg_values` for computed calibration values, `struct ti_iodelay_cfg` for one DT-provided pin delay tuple, `struct ti_iodelay_pingroup` for a generic pinctrl group plus its configurations, and `struct ti_iodelay_device` for device-local state. Important functions are `ti_iodelay_extract()`, `ti_iodelay_compute_dpe()`, `ti_iodelay_pinconf_init_dev()`, `ti_iodelay_pinconf_set()`, `ti_iodelay_dt_node_to_map()`, `ti_iodelay_node_iterator()`, `ti_iodelay_pinconf_group_set()`, `ti_iodelay_alloc_pins()`, and `ti_iodelay_probe()`. `dra7_iodelay_data` and `dra7_iodelay_regmap_config` provide the sole supported compatible, `ti,dra7-iodelay`.

## Control Flow

`module_platform_driver()` registers the platform driver. Probe requires an OF node, gets match data, maps the MMIO resource, initializes a regmap, unlocks the global IO delay block, registers a devm cleanup action that relocks it, reads reference/coarse/fine calibration registers, computes `cdpe` and `fdpe`, allocates synthetic pin descriptors from register-space geometry, registers the pinctrl device, and enables it.

When a consumer applies a pinctrl state, `ti_iodelay_dt_node_to_map()` counts rows in `pinctrl-pin-array`, allocates pins/config arrays, parses each row with `pinctrl_parse_index_with_args()`, converts the offset to a synthetic pin number, stores delay data in both the group and pin descriptor `drv_data`, registers a generic group, and returns one `PIN_MAP_TYPE_CONFIGS_GROUP` map. `ti_iodelay_pinconf_group_set()` accepts only one dummy config, `PIN_CONFIG_END`, and applies every `ti_iodelay_cfg` in the group through `ti_iodelay_pinconf_set()`.

## State and Persistence

Driver state is devm-managed and tied to the platform device lifetime: mapped base, regmap, pinctrl descriptor, pin descriptors, calibration values, and dynamically allocated groups/config arrays. Hardware state persists in IO delay registers after `regmap_update_bits()` writes. The driver deliberately leaves per-pin IO delay values unlocked to allow later mode changes such as MMC transitions, while the global block is relocked on device teardown through the devm cleanup action.

## Dependencies and Integration Points

It depends on OF, platform devices, `devm_platform_get_and_ioremap_resource()`, regmap MMIO, generic pinctrl groups, generic pinconf maps, and pinctrl devicetree helpers. It integrates with DRA7 Device Tree bindings using `pinctrl-pin-array`, with bootloader calibration because it reads recalibration values already programmed before Linux, and with debugfs via optional pin/group display callbacks.

## Risks

The delay math uses truncating integer division and assumes nonzero calibrated delay counts. Incorrect DT offsets can map to wrong synthetic pins, and `ti_iodelay_offset_to_pin()` checks only upper range, not that the offset is at or beyond `reg_start_offset` or aligned to a per-pin stride. `ti_iodelay_alloc_pins()` increments `phy_reg` but does not store names or physical addresses in descriptors, making debug names generic. `ti_iodelay_pinconf_group_set()` returns `-ENOTSUPP` for any per-pin write failure, losing the original regmap error. Leaving values unlocked is intentional but increases exposure to accidental padconf changes.

## Test Signals

Build under `PINCTRL_TI_IODELAY=y/m` and probe a `ti,dra7-iodelay` node with a valid MMIO resource. Runtime validation should cover valid and invalid `pinctrl-pin-array` rows, too few cells, out-of-range offsets, zero coarse/fine calibration counts, and representative MMC mode-change pinctrl states. Debugfs should show offsets, configured delays, and register values. Hardware tests should compare resulting coarse/fine fields against TRM calculations and confirm the global lock is restored on driver removal or probe-error cleanup.
