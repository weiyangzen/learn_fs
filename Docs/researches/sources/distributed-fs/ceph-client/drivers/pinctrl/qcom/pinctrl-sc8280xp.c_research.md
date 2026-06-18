# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp.c

## Purpose

`pinctrl-sc8280xp.c` is the Qualcomm SC8280XP TLMM pinctrl/GPIO driver data source for the shared MSM pinctrl core. It describes a large application-processor TLMM block with GPIOs, alternate functions, wake interrupt mapping, eGPIO support, two UFS reset groups, and SDC/QDSD groups. The file is almost entirely static SoC metadata plus the platform driver wrapper that registers the metadata with the common MSM pinctrl implementation.

## Important APIs, Types, and Data

- Uses `pinctrl-msm.h` and exports a `struct msm_pinctrl_soc_data` named `sc8280xp_pinctrl`.
- `PINGROUP()` generates normal GPIO-capable `struct msm_pingroup` records with eight mux slots, standard TLMM register offsets (`REG_SIZE * id`), GPIO input/output bits, IRQ bits, and eGPIO presence/enable bits.
- `SDC_QDSD_PINGROUP()` handles SD-card/QDSD groups with pull/drive configuration but no mux, GPIO, or IRQ capability.
- `UFS_RESET()` handles `ufs_reset` and `ufs1_reset` pseudo groups with output control at fixed offsets and no normal IRQ/mux fields.
- `sc8280xp_pins[]` contains GPIO descriptors and special non-GPIO descriptors up to the SDC groups.
- `DECLARE_MSM_GPIO_PINS()`, `enum sc8280xp_functions`, per-function `*_groups[]`, `sc8280xp_functions[]`, and `sc8280xp_groups[]` define the pin/function/group graph used by pinctrl clients.
- Function coverage includes QUP serial engines, I3C, QSPI, PCIe clock requests, USB/USB4 sideband pins, display hotplug and vsync, Ethernet MAC/RGMII, LPASS audio, QDSS, DDR test/debug functions, PRNG/PLL/test hooks, and eGPIO.
- `sc8280xp_pdc_map[]` maps many TLMM GPIO lines to PDC wake IRQ numbers.
- `sc8280xp_pinctrl` sets `.ngpios = 230`, includes the wake map, and sets `.egpio_func = 7`, matching `PINGROUP()`'s eGPIO mux slot placement and eGPIO register bit fields.
- OF matching binds `qcom,sc8280xp-tlmm`; the platform driver name is `sc8280xp-tlmm`.

## Control Flow

The driver registers at `arch_initcall()` with `platform_driver_register()`. OF matching instantiates the platform device for `qcom,sc8280xp-tlmm`. Probe is a thin wrapper that calls `msm_pinctrl_probe(pdev, &sc8280xp_pinctrl)`. From that point, the shared MSM core maps resources, registers the pinctrl device, GPIO chip, and IRQ support, and interprets the static tables when clients request pin states or GPIO operations. Module exit unregisters the platform driver.

## State and Persistence

This source stores no mutable driver-local state. Runtime state is held in the generic MSM pinctrl instance created during probe. Hardware configuration persists in TLMM registers. The static SoC table is not modified after compile time. eGPIO state is controlled through the common core using the mux slot and register bit metadata in each pingroup.

## Dependencies and Integration Points

The file depends on Linux platform/OF/module support and the common Qualcomm MSM pinctrl core. It integrates with SC8280XP device trees, pinctrl clients for serial, storage, display, USB, Ethernet, PCIe, debug, and audio peripherals, gpiolib users, and interrupt wake paths through PDC. The `.egpio_func` field and per-group `.egpio_enable`/`.egpio_present` bits require shared-core support for eGPIO handling.

## Risks and Edge Cases

- eGPIO support is table-driven and sensitive to mux slot numbering. `.egpio_func = 7` must match the final function slot in each relevant `PINGROUP()`.
- The file has a very large function/group surface. Typos in function names or group membership can break only one peripheral mode and may not be caught by generic compile tests.
- `.ngpios = 230` excludes the special SDC/UFS descriptors even though the pin array extends beyond ordinary GPIOs; off-by-one changes here can expose non-GPIO groups as GPIO lines or hide valid GPIOs.
- PDC wake map correctness is critical for suspend/resume wake behavior and is hard to verify without hardware.
- Special UFS and SDC groups intentionally disable many bit fields with `-1`; they must only be used through supported configuration paths.

## Test Signals

Build signals include successful compile with no missing `msm_mux_*` references and no initializer warnings. Runtime signals include successful probe for `qcom,sc8280xp-tlmm`, expected 230 GPIO lines exposed by gpiolib, debugfs visibility of functions and groups, pinctrl state application for QUP/I3C/QSPI/PCIe/USB/display/Ethernet/storage/audio clients, eGPIO selection tests where board hardware uses external GPIO functionality, and wake-from-suspend tests for GPIOs listed in `sc8280xp_pdc_map[]`.
