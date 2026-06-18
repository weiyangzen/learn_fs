# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660-lpass-lpi.c

## Purpose

`pinctrl-sdm660-lpass-lpi.c` describes the Qualcomm SDM660 LPASS Low Power Island pin controller variant for the shared LPI pinctrl driver. It exposes 32 LPI GPIOs and maps audio functions for PDM, DMIC, MCLK, comparator receive, and GPIO use. A source comment notes the driver is based on limited downstream information and requests schematic verification, which makes the table provenance an explicit research risk.

## Important APIs, Types, and Data

- Uses `pinctrl-lpass-lpi.h` and the LPI core macros/types.
- `enum lpass_lpi_functions` defines mux IDs for `comp_rx`, `dmic1_*`, `dmic2_*`, `mclk0`, `pdm_*`, `gpio`, and placeholder `__`.
- `sdm660_lpi_pinctrl_pins[]` defines `gpio0` through `gpio31`.
- Per-function group arrays map audio functions to pins: PDM clock/MCLK around `gpio18`, PDM sync/tx/rx around `gpio19` to `gpio25`, comparator RX on `gpio22`/`gpio24`, and DMIC functions on `gpio26` to `gpio29`.
- `sdm660_lpi_pinctrl_groups[]` uses `LPI_PINGROUP_OFFSET()` for every group, with explicit register offsets from `0x0000` through `0xb010`. Pins `0` to `17`, `30`, and `31` are described as GPIO-only/no alternate function in the table.
- `sdm660_lpi_pinctrl_functions[]` publishes the named alternate functions.
- `sdm660_lpi_pinctrl_data` sets `LPI_FLAG_SLEW_RATE_SAME_REG | LPI_FLAG_USE_PREDEFINED_PIN_OFFSET`, telling the core that slew configuration shares the same register and group offsets are precomputed rather than derived.
- OF match binds `qcom,sdm660-lpass-lpi-pinctrl`; the platform driver delegates probe/remove to the LPI core.

## Control Flow

The `module_platform_driver()` macro registers the platform driver. When a matching OF node appears, the platform bus invokes `lpi_pinctrl_probe`, which consumes `sdm660_lpi_pinctrl_data` from the match table. All pinctrl registration, GPIO registration, and register I/O are handled by the common LPI driver. Removal calls `lpi_pinctrl_remove`.

## State and Persistence

This file has only static variant metadata. Runtime state is allocated and owned by the LPI pinctrl core. LPASS LPI hardware registers hold the persistent pin mux/configuration state until reconfigured or reset. Because predefined offsets are used, the static offset table is effectively part of the hardware ABI for this variant.

## Dependencies and Integration Points

The source depends on the Linux platform and OF subsystems and on Qualcomm's LPI pinctrl implementation. It integrates with SDM660 audio DTS pinctrl consumers, especially PDM/DMIC capture/playback and MCLK users. The function and group names must match device-tree pin state names. The offset flags require the shared LPI core to interpret explicit offsets correctly.

## Risks and Edge Cases

- The explicit note about limited downstream information means mux assignments and offsets have higher validation risk than table data sourced from full documentation.
- `LPI_FLAG_USE_PREDEFINED_PIN_OFFSET` makes each offset entry critical; any typo routes register writes to the wrong pin.
- Many pins are GPIO-only placeholders with explicit offsets. Clients selecting unavailable alternate functions should fail rather than silently misconfigure.
- `LPI_FLAG_SLEW_RATE_SAME_REG` changes how the core writes slew fields; using the wrong flag can corrupt unrelated config bits.
- Audio failures may be topology-specific, for example PDM RX lanes on `gpio21`, `gpio23`, and `gpio25` may need separate board-level validation.

## Test Signals

Compile tests should verify all macro references resolve. Runtime tests should verify probe of `qcom,sdm660-lpass-lpi-pinctrl`, pinctrl debugfs pin/function visibility, GPIO-only pins behaving as GPIOs, and audio validation for PDM clock/sync/tx/rx, DMIC1/DMIC2, comparator RX, and MCLK0. Register trace or hardware readback is especially useful because this variant depends on predefined offsets.
