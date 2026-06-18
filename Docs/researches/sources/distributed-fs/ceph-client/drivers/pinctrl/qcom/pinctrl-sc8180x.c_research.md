# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8180x.c

## Purpose

`pinctrl-sc8180x.c` is the Qualcomm SC8180x TLMM pinctrl/GPIO description consumed by the shared MSM pinctrl core. It describes the SoC's TLMM pin numbers, alternate mux functions, GPIO register layout, tile placement, special SD/UFS groups, wake interrupt mapping, and DT/ACPI platform binding. The file is data-heavy, but it also has an SC8180x-specific ACPI resource-splitting probe path because ACPI firmware exposes TLMM as one memory resource while the shared MSM core expects named tile resources.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and publishes `struct msm_pinctrl_soc_data` instances for the generic Qualcomm MSM pinctrl driver.
- `sc8180x_tiles[]` names the three TLMM tiles: `south`, `east`, and `west`; the tile enum indexes the same names.
- `struct tile_info` and `sc8180x_tile_info[]` record ACPI-only offsets/sizes used to split a monolithic TLMM memory range into tile resources.
- `PINGROUP_OFFSET()` and `PINGROUP()` generate ordinary `struct msm_pingroup` entries with mux, pull, drive, output-enable, input/output, and interrupt bit positions. `PINGROUP_OFFSET()` handles banks whose register offsets do not match the simple `REG_SIZE * id` pattern.
- `SDC_QDSD_PINGROUP()` describes non-GPIO SD-card/QDSD pin groups with no mux or interrupt support and fixed pull/drive bit fields.
- `UFS_RESET()` describes the UFS reset pseudo group with output control but no normal mux/interrupt fields.
- `sc8180x_pins[]`, `DECLARE_MSM_GPIO_PINS()`, per-function `*_groups[]`, `enum sc8180x_functions`, `sc8180x_functions[]`, and `sc8180x_groups[]` form the pinctrl core's visible pin, function, and group database.
- `sc8180x_acpi_reserved_gpios[]` reserves firmware-owned GPIOs for ACPI operation.
- `sc8180x_pdc_map[]` maps GPIO lines to PDC wake interrupt lines.
- `sc8180x_pinctrl` is the DT data path: pins, functions, groups, 191 GPIOs, tile names, and wake map.
- `sc8180x_acpi_pinctrl` is the ACPI data path: pins, groups, reserved GPIOs, 190 GPIOs, and tile names, but no function table or PDC wake map.
- `sc8180x_pinctrl_of_match[]` binds `qcom,sc8180x-tlmm`; `sc8180x_pinctrl_acpi_match[]` binds ACPI ID `QCOM040D` with driver data pointing at the ACPI SoC data.

## Control Flow

The platform driver is registered at `arch_initcall()` by `sc8180x_pinctrl_init()` and unregistered by the module exit function. Probe calls `device_get_match_data()` to choose the DT or ACPI `msm_pinctrl_soc_data`; if no match data exists, probe fails with `-EINVAL`.

Before handing off to `msm_pinctrl_probe()`, probe runs `sc8180x_pinctrl_add_tile_resources()`. For DT nodes, that helper returns immediately because DT already models the TLMM tiles as separate resources. For ACPI devices, it allocates a replacement resource table, copies non-memory resources, finds the single memory resource, creates three named tile memory resources by applying `sc8180x_tile_info[]`, inserts those resources into the parent resource tree, removes the original monolithic memory resource, and installs the new resource table with `platform_device_add_resources()`. After this transformation, the shared MSM core can map tiles as if firmware had described them natively.

After resource preparation, all pinctrl, pinmux, GPIO, and IRQ behavior is delegated to the MSM core through `msm_pinctrl_probe()`.

## State and Persistence

The driver has no runtime-persistent state of its own beyond static const tables and the devm-allocated ACPI replacement resources. Pin configuration, direction, mux, drive strength, pull, GPIO data, and interrupt configuration persist in TLMM hardware registers managed through the shared core. ACPI probing mutates the platform device resource list for the lifetime of the device, replacing a firmware-provided single memory resource with three named tile resources. The source's static SoC data is shared across probes and is not dynamically modified.

## Dependencies and Integration Points

This file depends on the Linux platform bus, OF/ACPI matching, resource management, and `drivers/pinctrl/qcom/pinctrl-msm.*`. Its tables must match Qualcomm SC8180x TLMM hardware and the binding names consumed by device trees or ACPI tables. It integrates with the generic pinctrl, pinmux, gpiochip, and irqchip paths exposed by the MSM core. Wake behavior depends on correct GPIO-to-PDC mapping. ACPI behavior depends on `device_get_match_data()` returning the `kernel_ulong_t` driver data from the ACPI table and on safe resource-tree surgery before `msm_pinctrl_probe()`.

## Risks and Edge Cases

- The ACPI resource split is the main behavioral risk: incorrect offsets/sizes or resource-tree insertion/removal failures can break all TLMM register mappings on ACPI systems.
- `insert_resource()` return values are ignored; conflicts in the resource tree may go unnoticed before the old resource is removed.
- DT and ACPI data differ: ACPI omits the function table and wake map and reserves several GPIOs. Any shared-core assumption that functions or wake data always exist could affect ACPI operation.
- The table is large and index-sensitive. Pin array indexes, `gpioN_pins`, group array order, function enum values, and `msm_mux_*` names must remain aligned.
- `PINGROUP_OFFSET()` encodes many nonuniform offsets near the end of the GPIO range. A wrong offset can silently target the wrong register block.
- Special SD/UFS groups have many bit fields set to `-1`; consumers must treat them as limited-capability groups.
- Wake entries include duplicate GPIOs mapped to multiple PDC lines, so wake handling must preserve all intended rows.

## Test Signals

Useful build signals are `W=1`/sparse checks for table initializer mistakes, successful module/platform driver compilation with OF and ACPI enabled, and absence of missing `msm_mux_*` symbols. Runtime signals include successful probe for `qcom,sc8180x-tlmm` DT systems, successful ACPI probe for `QCOM040D`, named tile resources visible to the shared core, GPIO line count/reservation behavior matching firmware expectations, pinmux state application from device tree, GPIO direction/value tests through gpiolib, and wake-capable GPIO suspend/resume tests using the PDC map.
