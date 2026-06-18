<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h

## Purpose
This header declares the DSI VBT initialization, GPIO setup, sequence execution, and parameter logging APIs.

## Important APIs, Types, and Functions
It forward declares `enum mipi_seq` and `struct intel_dsi`, then exposes `intel_dsi_vbt_init()`, `intel_dsi_vbt_gpio_init()`, `intel_dsi_vbt_exec_sequence()`, and `intel_dsi_log_params()`.

## Control Flow
There is no local implementation flow. Callers use it during DSI encoder setup to initialize VBT-derived fields, set up panel GPIO ownership, execute panel power/backlight sequences, and log resolved parameters.

## State and Persistence Behavior
No state is defined here. The implementation mutates `struct intel_dsi` and connector panel VBT-derived state.

## Dependencies and Integration Points
The header bridges platform DSI encoder code with VBT parsing and sequence execution. It keeps MIPI sequence details behind the implementation while allowing callers to name sequence IDs.

## Risks
Callers must only execute sequences after VBT data and DSI hosts are initialized. Passing the wrong `panel_id` or executing sequences out of power order can leave panels unresponsive.

## Test Signals
Compile coverage, DSI init paths calling `intel_dsi_vbt_init()` before sequence execution, and panel bring-up logs from `intel_dsi_log_params()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h -->
