# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynqmp.c

## Purpose
Implements the Xilinx ZynqMP and Versal pinctrl driver using firmware platform-management APIs instead of direct MMIO. It discovers pins, functions, groups, and group membership from firmware, then services mux and config requests by calling firmware pinctrl operations.

## Important APIs, Types, And Functions
Key types are `struct zynqmp_pinctrl`, `struct zynqmp_pmux_function`, and `struct zynqmp_pctrl_group`. Important paths include `zynqmp_pinmux_request_pin()`, `zynqmp_pinmux_set_mux()`, `zynqmp_pinmux_release_pin()`, `zynqmp_pinconf_cfg_get()`, `zynqmp_pinconf_cfg_set()`, `zynqmp_pinctrl_prepare_pin_desc()`, `versal_pinctrl_prepare_pin_desc()`, `zynqmp_pinctrl_prepare_function_info()`, and `zynqmp_pinctrl_probe()`.

## Control Flow
Probe queries the SoC family, prepares pin descriptors differently for ZynqMP and Versal, discovers the number of functions, each function name, each function's group count, group-to-pin membership, and function-to-group names, then registers the pinctrl device. Mux request/release and set_mux call `zynqmp_pm_pinctrl_request()`, `zynqmp_pm_pinctrl_release()`, and `zynqmp_pm_pinctrl_set_function()`. Pinconf get/set translates generic pinconf parameters to PM firmware config IDs and drive-strength encodings.

## State And Persistence
Persistent hardware state lives in platform firmware and pin controller registers managed by firmware. Driver state is dynamically allocated arrays of pin descriptors, function descriptors, and group descriptors. `family_code` and the global `zynqmp_desc` hold family-dependent descriptor state.

## Dependencies And Integration Points
Depends on `<linux/firmware/xlnx-zynqmp.h>`, PM query IDs, DT compatibles `xlnx,zynqmp-pinctrl` and `xlnx,versal-pinctrl`, generic DT pinconf parsing, and `pinctrl_utils_free_map`. Versal also requires firmware support for `PM_QID_PINCTRL_GET_ATTRIBUTES`.

## Risks
Firmware response correctness is critical; group IDs index directly into allocated arrays. `MAX_GROUP_PIN`, `MAX_PIN_GROUPS`, and response chunk sizes bound discovery. Versal pin numbers use firmware attributes and non-ZynqMP code adjusts pin bitmap indexes by subtracting one, which is a subtle family-specific path. `zynqmp_pinconf_cfg_set()` logs failures per config but returns 0 after the loop, so callers may not see firmware set failures.

## Test Signals
Probe on ZynqMP and Versal firmware, PM query failure injection, mux request/set/release traces, DT pinconf application for pull, slew, Schmitt, drive strength, tristate, and output enable, and validation that discovered group/function names match firmware expectations are key signals.
