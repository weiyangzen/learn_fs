<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c

## Purpose
This file translates VBT MIPI panel data into runtime DSI encoder parameters, executes BIOS-defined MIPI panel sequences, and handles platform-specific GPIO/I2C/PMIC side effects needed for panel power and backlight control.

## Important APIs, Types, and Functions
Public functions are `intel_dsi_vbt_init()`, `intel_dsi_vbt_gpio_init()`, `intel_dsi_vbt_exec_sequence()`, and `intel_dsi_log_params()`. Internal sequence executors handle send-packet, delay, GPIO, I2C, SPI skip, and PMIC elements through `exec_elem[]`. GPIO helpers cover SoC GPIO lookup, opaque VLV/CHV lookup tables, BXT GPIOs, and ICL native GPIO registers. ACPI I2C helpers map VBT target addresses to Linux I2C adapters when available.

## Control Flow
`intel_dsi_vbt_init()` copies fields from `mipi_config` and PPS data into `intel_dsi`, converts VBT pixel format, adjusts pixel clock for dual-link and burst mode, validates target burst frequency, converts delays from 100us units to milliseconds, initializes I2C bus selection, and attaches the manually allocated DSI devices.

`intel_dsi_vbt_exec_sequence()` wraps a sequence with optional GPIO panel/backlight toggles and calls `intel_dsi_vbt_exec()`. The executor skips the sequence id and optional size, then loops through elements until `MIPI_SEQ_ELEM_END`, dispatching each operation and verifying the consumed size for sequence versions with explicit lengths.

## State and Persistence Behavior
VBT-derived DSI fields persist in `struct intel_dsi`. Sequence data itself is stored in `connector->panel.vbt.dsi.sequence`. GPIO descriptor caching includes a static SoC GPIO table and per-encoder `gpio_panel`/`gpio_backlight` handles. `intel_dsi->i2c_bus_num` starts at `-1` and is lazily resolved on first I2C sequence operation.

## Dependencies and Integration Points
The implementation depends on VBT panel data, DRM MIPI DSI packet helpers, GPIO descriptor lookup tables, pinctrl mappings, ACPI I2C resource parsing, PMIC opregion support, VLV/CHV sideband behavior, ICL display GPIO registers, PPS registers, and platform DSI FIFO helpers. It integrates tightly with `intel_dsi.h` state and panel initialization.

## Risks
VBT sequence formats vary by version; unsupported operations without a size cannot be skipped safely. Unaligned casts from byte streams make endianness and alignment assumptions, although PMIC paths use explicit unaligned helpers. GPIO numbering differs by platform and sequence version, and some paths are marked as hacks or unclear. Missing `CONFIG_PMIC_OPREGION` can make required hardware sequences fail. Burst-mode clock validation can reject panels with bad VBT data.

## Test Signals
Signals include successful DSI panel power-on/off sequences, debug logs for expected MIPI operations, correct dual-link and burst pclk calculation, GPIO toggles on VLV/CHV/BXT/ICL panels, ACPI I2C adapter resolution, PMIC sequence execution when required, and no inconsistent operation-size errors on supported VBT sequence versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c -->
