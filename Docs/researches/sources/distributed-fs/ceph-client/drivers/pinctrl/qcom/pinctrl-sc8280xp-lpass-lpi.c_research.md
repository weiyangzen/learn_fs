# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp-lpass-lpi.c

## Purpose

`pinctrl-sc8280xp-lpass-lpi.c` describes the Low Power Island LPASS audio pin controller for Qualcomm SC8280XP. It is a compact variant table for the shared `pinctrl-lpass-lpi` driver, covering 19 LPI GPIOs used by SoundWire, DMIC, I2S/MI2S, WSA SoundWire, and external MCLK functions. The file contains no custom register access or probe logic; all behavior is delegated to the generic LPI pinctrl core.

## Important APIs, Types, and Data

- Includes `pinctrl-lpass-lpi.h`, which provides `struct lpi_pingroup`, `struct lpi_function`, `struct lpi_pinctrl_variant_data`, `LPI_PINGROUP()`, and `LPI_FUNCTION()`.
- `enum lpass_lpi_functions` defines mux IDs for the exported audio functions plus `gpio` and placeholder `__` entries used by the macro-generated group tables.
- `sc8280xp_lpi_pins[]` exposes pins `gpio0` through `gpio18`.
- Per-function group arrays map function names to legal pin names, for example `swr_tx_data` on `gpio1`, `gpio2`, and `gpio14`, `qua_mi2s_data` on `gpio2` through `gpio5`, and `ext_mclk1_*` on selected pins.
- `sc8280xp_groups[]` defines one `LPI_PINGROUP()` per pin. The second macro argument is either a slew-rate register selector/offset or `LPI_NO_SLEW`. The function slots encode the mux alternatives accepted by the shared LPI core.
- `sc8280xp_functions[]` lists each selectable function with `LPI_FUNCTION()`.
- `sc8280xp_lpi_data` packages pins, groups, and functions for the generic driver.
- `lpi_pinctrl_of_match[]` binds `qcom,sc8280xp-lpass-lpi-pinctrl` and attaches `sc8280xp_lpi_data`.
- `lpi_pinctrl_driver` uses `lpi_pinctrl_probe` and `lpi_pinctrl_remove` directly.

## Control Flow

`module_platform_driver(lpi_pinctrl_driver)` registers the platform driver. Matching is OF-only. On probe, the generic LPI probe reads the matched variant data pointer, registers pinctrl/pinmux/gpio resources, and uses this file's static tables to service mux and configuration requests. Remove is delegated to `lpi_pinctrl_remove`.

## State and Persistence

This file holds only immutable descriptor tables. Runtime state, register mappings, GPIO chip state, and pinctrl handles are owned by the shared LPI core and device-managed resources. Pin mux and configuration settings persist in LPASS LPI hardware registers until changed or reset.

## Dependencies and Integration Points

The driver depends on the platform bus, OF matching, Linux module infrastructure, gpiolib, and the Qualcomm LPI pinctrl core. It integrates with SC8280XP audio device-tree nodes that reference the LPI pinctrl provider for SoundWire, DMIC, I2S, MI2S, WSA, and MCLK pin states. Function/group names must match binding and board DTS usage.

## Risks and Edge Cases

- The table relies on exact mux-slot ordering expected by LPI hardware; wrong slot placement can select the wrong audio function.
- Several pins share related functions, such as SoundWire data lanes and MI2S data lanes, so a group membership error may only appear when a specific audio topology is enabled.
- `LPI_NO_SLEW` pins cannot be slew-configured; DTS states expecting slew control on those pins would not behave as intended.
- There is no custom validation in this file, so errors are usually discovered as failed audio routing, failed pin state selection, or silent hardware misconfiguration.

## Test Signals

Build coverage should confirm all `LPI_MUX_*` symbols referenced by `LPI_PINGROUP()` exist and the variant data compiles. Runtime signals include successful probe of `qcom,sc8280xp-lpass-lpi-pinctrl`, expected pins/functions under debugfs pinctrl output, successful application of board audio pinctrl states, and audio path tests for SoundWire, DMIC, I2S/MI2S, WSA, and MCLK consumers.
