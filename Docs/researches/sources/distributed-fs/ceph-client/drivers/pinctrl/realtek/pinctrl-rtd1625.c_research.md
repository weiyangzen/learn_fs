# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1625.c

## Purpose
This file is the Realtek RTD1625 SoC-specific pin controller description. It does not implement generic pinctrl algorithms itself; instead it builds static tables that describe four RTD1625 pin-control register banks and hands the matching descriptor to the shared Realtek pinctrl core in `pinctrl-rtd.h`/the companion core implementation. The supported banks are `iso`, `isom`, `ve4`, and `main2`, each exposed by its own device-tree compatible string.

## Important APIs, Types, And Data
- `enum rtd1625_*_pins_enum` assigns dense pin IDs for each bank. These enum values are used as indexes into pin, mux, and config arrays, so ordering is a behavioral contract.
- `struct pinctrl_pin_desc rtd1625_*_pins[]` publishes pin names to the Linux pinctrl core.
- `DECLARE_RTD1625_PIN()` creates one-pin arrays used by group descriptors.
- `struct rtd_pin_group_desc rtd1625_*_pin_groups[]` maps named groups to pin arrays.
- `struct rtd_pin_func_desc rtd1625_*_pin_functions[]` maps function names to group-name lists via `RTD1625_FUNC()`.
- `struct rtd_pin_desc rtd1625_*_muxes[]` is the core mux data: each `RTK_PIN_MUX()` entry names the affected pin, register offset, bit mask, and legal `RTK_PIN_FUNC()` encoded values.
- `struct rtd_pin_config_desc rtd1625_*_configs[]` and `struct rtd_pin_sconfig_desc rtd1625_*_sconfigs[]` describe pin configuration register fields, including pull, drive, and special drive-strength data.
- `struct rtd_reg_range`/`struct rtd_pin_range` constrain the register windows that the generic Realtek core may access for each bank.
- `struct rtd_pinctrl_desc rtd1625_*_pinctrl_desc` is the final per-bank descriptor consumed by `rtd_pinctrl_probe()`.

## Control Flow And Integration
The runtime path is deliberately short. The platform driver matches one of:
`realtek,rtd1625-iso-pinctrl`, `realtek,rtd1625-isom-pinctrl`, `realtek,rtd1625-ve4-pinctrl`, or `realtek,rtd1625-main2-pinctrl`. `rtd1625_pinctrl_probe()` calls `device_get_match_data()` to fetch the selected `rtd_pinctrl_desc`, then delegates to `rtd_pinctrl_probe(pdev, desc)`. The shared Realtek driver is responsible for registering the pinctrl device, decoding device-tree pin states, applying mux values, applying pin config, and using `realtek_pinctrl_pm_ops` for suspend/resume behavior.

The descriptor tables define the SoC surface:
- `iso` covers low-power/isolated pins, USB-CC pins, SDIO, many audio and video functions, EJTAG location selectors, RGMII/CSI voltage selectors, SPDIF mode/location selectors, and register ranges at offsets `0x0..0x58`, `0x120..0x130`, `0x180..0x18c`, and `0x1a0..0x1ac`.
- `isom` covers a small isolated management bank with GPIO0/1/28/29, IR receive location, UART10, pctrl, debug output, and tristate.
- `ve4` covers a broad media/peripheral bank: UART, GSPI, I2C, SD, TS, CSI, PCIe indicators, SPDIF, Ethernet LED/PHY alternate locations, PWM, and a `ve4_uart_loc` selector.
- `main2` covers eMMC, NAND, SD/HIF, Ethernet RGMII/RMII/LED/PHY, I2C1, SPI, debug, PLL test, and legacy EJTAG/HI function choices.

## State And Persistence
This file declares only immutable `static const` tables plus the platform driver object. Persistent hardware state lives in RTD1625 pinmux/config registers after the shared Realtek core writes encoded mux/config values. The file's own state is limited to module registration through `module_platform_driver()`. Suspend/resume persistence is delegated through `.pm = &realtek_pinctrl_pm_ops`; the register ranges included in each descriptor are the likely save/restore boundaries for the common core.

## Dependencies
It depends on Linux platform-driver, OF matching, module, and pinctrl headers, and on local Realtek abstractions from `pinctrl-rtd.h`: `rtd_pinctrl_desc`, `rtd_pin_desc`, `rtd_pin_config_desc`, `RTK_PIN_MUX`, `RTK_PIN_FUNC`, `RTK_PIN_CONFIG*`, `RTK_PIN_SCONFIG`, `SHIFT_LEFT`, `PADDRI_4_8`, and `realtek_pinctrl_pm_ops`.

## Risks And Review Notes
- The dense enum indexes must match all sparse designated initializer arrays. Adding/removing pins without updating mux/config arrays can silently leave pins without mux/config support.
- Function group lists are string-based. A typo is not caught by the C type system. One notable review signal is `rtd1625_iso_spdif_in_coaxial_groups`, which references `"spdif_sel"` while the visible selector pins are named `spdif_loc` and `spdif_in_mode`; this should be checked against the shared Realtek group lookup behavior and binding expectations.
- Several mux fields accept wide or unusual encoded values, such as `RTD1625_ISO_GPIO_112` using `GENMASK(4, 0)` and values beyond `0xf`. Mask/value alignment is critical.
- Register range declarations must include every offset referenced by mux/config/sconfig tables. Missing a range can break PM save/restore or access validation in the common core.
- Many pins share the same physical groups across mutually exclusive functions. Bad DT pin states can disrupt boot-critical busses such as eMMC, SDIO, RGMII/RMII, I2C, or UART.

## Test Signals
Useful validation includes `dtbs_check` for RTD1625 pinctrl compatibles and pin-state names, `make W=1`/`COMPILE_TEST` builds for array/type issues, boot logs showing `rtd1625-pinctrl` probe for all instantiated banks, debugfs pinctrl inspection to verify registered pins/groups/functions, and hardware tests that switch representative muxes for eMMC, SDIO, UART, I2C, Ethernet, audio, and video pins. Suspend/resume tests should verify that mux and config registers are restored for all listed register ranges.
