# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp.h

## Purpose
This is the central public firmware API definition for Xilinx ZynqMP, Versal, and Versal NET platform management. It enumerates firmware command ids, status codes, reset ids, pinctrl/clock/query controls, node capabilities, FPGA loading, secure register access, suspend/shutdown modes, and PM call wrappers.

## APIs, types, and control flow
The primary low-level gateways are `zynqmp_pm_invoke_fn()` and `zynqmp_pm_invoke_fw_fn()`, taking PM API ids and variadic payloads. High-level wrappers cover API/chip/family discovery, clock enable/disable/divider/parent, PLL fractional mode/data, SD/GEM config, resets, boot mode, suspend mode, node request/release/requirements, efuse, FPGA load/status/config status, global/persistent global storage registers, tap delay, system shutdown, pinctrl, PDI load, notifier registration, feature checks/config, secure register read/mask-write, SGI registration, powerdown/wake, RPU mode/TCM config, and node status. When firmware is unavailable, wrappers return `-ENODEV`.

## State and dependencies
State is firmware-owned but Linux caches/uses constants for API versions, module ids, callback payload widths, node ids, reset ids, and PM return statuses. The header includes UFS and crypto sub-APIs and is consumed by clock, pinctrl, reset, FPGA, power, UFS, crypto, and event drivers.

## Integration, risks, and tests
Risks include API id drift, wrong enum/node id selection, insufficient feature checks before optional calls, output pointer misuse after errors, variadic argument count mistakes in the invoke layer, and firmware version mismatch. Tests should validate disabled stubs, feature discovery, each subsystem wrapper's argument packing, reset/status paths, clock tree queries, pinctrl config, FPGA load flags, shutdown commands, and conversion of firmware return codes to Linux errors.
