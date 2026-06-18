# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd1319d.c

## Purpose
Provides the Realtek RTD1319D ISO pin bank description for the shared Realtek DHC pinctrl core. It maps RTD1319D package pins and selector pseudo-pins to Linux pinctrl groups, functions, mux register fields, pin configuration fields, and special drive-strength fields, then registers a small platform driver for `realtek,rtd1319d-pinctrl`.

## Important APIs, Types, and Functions
`enum rtd13xxd_iso_pins` defines the pin-number namespace, including GPIO0-64, USB CC pins, HIF pins, UART0 pins, eMMC pins, selector pins for UART2/GSPI/HI/SF/EJTAG/DMIC/VTC/audio/SPDIF/HIF/smart-card routing, and boot/reset/test pins. `rtd1319d_iso_pins` exposes those names to the kernel pinctrl framework. `rtd1319d_pin_groups` is generated from one-pin arrays using `DECLARE_RTD1319D_PIN` and `RTD1319D_GROUP`.

`rtd1319d_pin_functions` is the function catalog. It includes baseline GPIO/NF/eMMC plus RTD1319D-specific routes for transport-stream pins (`tp0`, `tp1`), smart-card interfaces (`sc0`, `sc1`, and data selectors), AO pins, GSPI, UARTs, I2C0/1/3/4/5, PCIe1, SDIO, Ethernet LED/PHY, SPI, PWM loc variants, QAM AGC, SPDIF loc variants, VFD, SD/HIF, DMIC/audio/VTC, DC fan, PLL test, EJTAG for SCPU/ACPU/VCPU/SECPU/AUCPU, debug outputs, standby debug, and PMIC power-up. The descriptor `rtd1319d_iso_pinctrl_desc` passes all tables to `rtd_pinctrl_probe()`.

## Control Flow
`rtd1319d_pinctrl_init()` registers a platform driver at `arch_initcall`. On DT match, `rtd1319d_pinctrl_probe()` delegates to the shared Realtek probe. The common core uses `rtd1319d_iso_pinctrl_desc` to publish groups and functions, and later services mux/config requests by direct pin-number indexing into `rtd1319d_iso_muxes` and `rtd1319d_iso_configs`.

Mux control is declarative: each populated `RTK_PIN_MUX()` entry names a pin, gives a mux register offset and mask, and lists accepted function-name/value pairs. Selector pseudo-pins such as `ur2_loc`, `gspi_loc`, `spdif_loc`, `sc0_loc`, and `sc1_loc` are modeled as pinctrl groups too, so selecting a routed function can program both the data pins and the selector field. Pinconf control is similarly declarative through `RTK_PIN_CONFIG()` and `RTK_PIN_SCONFIG()` entries for bias, Schmitt, coarse drive strength, power source, and custom P/N drive and duty-cycle fields.

## State and Persistence Behavior
The file contains only constant tables plus platform-driver registration. It does not allocate state, persist data outside hardware registers, or implement suspend/resume logic. Runtime MMIO and regmap state are owned by the shared core. `rtd1319d_iso_pinctrl_desc` does not provide `.pin_range`, and the platform driver has no `.pm` pointer, so the common save/restore implementation is not active for this variant.

## Dependencies and Integration Points
The file depends on `pinctrl-rtd.h`, Linux pinctrl descriptors, platform drivers, OF matching, and module alias support. It is built by `CONFIG_PINCTRL_RTD1319D`, which depends on `CONFIG_PINCTRL_RTD`. Board integration occurs through DT pinctrl states that use the function and group names from this file. The driver is an integration point for storage (eMMC/NF/SD/SDIO/SPI), low-speed serial (UART/I2C/GSPI/smart-card), networking pins, audio pins, USB Type-C CC pins, PCIe, debug/JTAG, and board-control pins.

## Risks
The descriptor relies on dense-enough enum values matching sparse static arrays. Any pin-number reorder or missing designated initializer can redirect mux/config writes to the wrong register description. Group and function names are string-coupled; misspellings between function group arrays and per-pin `RTK_PIN_FUNC()` entries produce runtime mux failures only when a DT state or GPIO request tries that path.

Some entries deliberately model route selectors as pseudo-pins rather than package pins. Those selectors can be easy to omit from a DT pinctrl state: for example, smart-card data, UART2 location, GSPI location, SPDIF location, and EJTAG target location often require programming both data pins and selector fields. `RTD1319D_ISO_GPIO_DUMMY_77` appears in the pin list as `"dummy"` but is not declared as a group, which is intentional but makes pin-count and enum maintenance more fragile. `rtd1319d_iso_muxes` ends with an explicit zero entry for `TESTMODE`; unsupported muxes return success without programming when the common core sees no mux name, so missing table coverage can be silent for GPIO requests.

## Test Signals
Compile and module-alias checks should cover `CONFIG_PINCTRL_RTD1319D` and the `realtek,rtd1319d-pinctrl` compatible. Probe tests should verify MMIO resource mapping and pinctrl registration. Functional tests should exercise eMMC/NF, GPIO fallback, UART0/1/2 with selector disable/loc0/loc1, GSPI selector paths, I2C0/1/3/4/5, SDIO, SD/HIF, smart-card SC0/SC1 data selectors, SPI, PWM loc variants, QAM AGC, VFD, SPDIF loc variants, USB CC, audio/DMIC/VTC selectors, and each EJTAG disable/location selector including SECPU. Pinconf tests should cover both simple GPIO-style 4/8 mA pins and eMMC/HIF/SDIO-style sconfig pins. Negative tests should intentionally request unsupported pin configs, unsupported function names, and selector-less routed functions to confirm errors or observable misrouting in debug output.
