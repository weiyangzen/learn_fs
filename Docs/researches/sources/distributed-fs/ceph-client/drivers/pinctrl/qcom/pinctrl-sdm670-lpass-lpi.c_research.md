# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670-lpass-lpi.c

## Purpose

`pinctrl-sdm670-lpass-lpi.c` describes the Qualcomm SDM670 LPASS LPI pin controller variant for the shared LPI pinctrl driver. It exposes 32 LPI GPIOs and audio/control functions including PDM, DMIC, I2S1, SLIMbus clock, MCLK0, comparator receive, and an LPASS codec reset function. It is a static descriptor file with no custom probe logic.

## Important APIs, Types, and Data

- Includes `pinctrl-lpass-lpi.h`.
- `enum lpass_lpi_functions` declares mux IDs for `comp_rx`, `dmic1_*`, `dmic2_*`, `i2s1_*`, `lpi_cdc_rst`, `mclk0`, `pdm_*`, `slimbus_clk`, `gpio`, and placeholder `__`.
- `sdm670_lpi_pinctrl_pins[]` defines pins `gpio0` through `gpio31`.
- Per-function group arrays bind functions to pins: I2S1 on `gpio8` to `gpio11`, SLIMbus clock on `gpio18`, MCLK/PDM around `gpio19` to `gpio25`, DMIC on `gpio26` to `gpio29`, and `lpi_cdc_rst` on `gpio29`.
- `sdm670_lpi_pinctrl_groups[]` contains one `LPI_PINGROUP()` per pin; many early and trailing pins expose no alternate functions, while audio-capable pins include one or more mux slots.
- `sdm670_lpi_pinctrl_functions[]` publishes the alternate functions to pinctrl clients.
- `sdm670_lpi_pinctrl_data` provides pins/groups/functions and sets `LPI_FLAG_SLEW_RATE_SAME_REG`.
- OF matching binds `qcom,sdm670-lpass-lpi-pinctrl`, with probe/remove delegated to the LPI core.

## Control Flow

The platform driver is registered via `module_platform_driver()`. On OF match, `lpi_pinctrl_probe` consumes the variant data and registers the provider. Pin state selection, GPIO operations, and register access are implemented by the common LPI pinctrl core. Remove is handled by `lpi_pinctrl_remove`.

## State and Persistence

This source is immutable table data only. Device state lives in the generic LPI core instance. Pin settings persist in LPASS LPI hardware registers. The slew-rate flag changes core write behavior but no local state is updated in this file.

## Dependencies and Integration Points

The driver depends on platform/OF/module support and the Qualcomm LPI pinctrl core. It integrates with SDM670 audio and codec-related device-tree pin states. Function/group names are part of the DTS-facing ABI for audio routing and codec reset control.

## Risks and Edge Cases

- `gpio29` supports both `dmic2_data` and `lpi_cdc_rst`; board pin states must choose the correct mux for the audio or reset use case.
- `LPI_FLAG_SLEW_RATE_SAME_REG` must match hardware layout; otherwise configuration writes may affect the wrong bits.
- Many GPIOs have no alternate functions, so attempting to use them for unsupported audio routes should fail predictably.
- Audio table errors may not show in generic GPIO tests; they require active audio/codec pin states.

## Test Signals

Build checks should catch unresolved LPI mux names. Runtime signals include successful probe for `qcom,sdm670-lpass-lpi-pinctrl`, expected 32 pins in debugfs, correct function/group listings, and board-level validation of I2S1, PDM, DMIC, SLIMbus clock, MCLK0, comparator RX, and codec reset pin states.
