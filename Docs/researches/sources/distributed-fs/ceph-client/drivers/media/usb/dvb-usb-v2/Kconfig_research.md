# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/Kconfig

## Purpose

This `Kconfig` file defines the build-time configuration menu for the second-generation DVB USB driver framework and the individual USB receiver drivers that sit on top of it. It lets kernel builders enable the shared `DVB_USB_V2` core and then select device-specific drivers such as AF9015, AF9035, Anysee, RTL28xxU, MxL111SF, and others.

## Important APIs, Types, and Symbols

`config DVB_USB_V2` is the umbrella tristate. It depends on `DVB_CORE`, `USB`, `I2C`, and either `RC_CORE` or no RC support. Its help text points users to firmware requirements and supported-device documentation.

Inside `if DVB_USB_V2`, each device driver gets a tristate symbol. `DVB_USB_AF9015` depends on `DVB_USB_V2 && I2C_MUX`, selects `REGMAP` and `DVB_AF9013`, and conditionally selects tuner/front-end helpers under `MEDIA_SUBDRV_AUTOSELECT`. Other symbols express similar dependencies, including hard dependencies such as `RC_CORE` for `DVB_USB_LME2510` and conditional SDR support for `DVB_USB_RTL28XXU`.

## Control Flow

Kconfig has declarative dependency flow. Enabling `DVB_USB_V2` makes the child choices visible. Enabling a child symbol controls which object targets the Makefile builds and which frontend/tuner modules are selected automatically. Conditional `select` clauses reduce manual configuration burden when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## State and Persistence Behavior

The file persists configuration state through kernel `.config` symbols. At runtime it has no state, but selected symbols determine which modules exist, which firmware names are requested, and which probe tables can bind to USB devices.

## Dependencies and Integration Points

This file integrates with `drivers/media/usb/dvb-usb-v2/Makefile`, the DVB core, USB core, I2C, rc-core, regmap, DVB frontend drivers, tuner drivers, and media-subdriver autoselection. For AF9015 specifically, its Kconfig entry enables the code in `af9015.c` and ensures the AF9013 demodulator and relevant tuner drivers can be built.

## Risks

Incorrect dependencies can produce link failures, missing symbols, or unusable drivers that compile without required subdrivers. Overbroad `select` usage can force in dependencies unexpectedly, while missing conditional selects can leave common hardware unsupported unless users know which tuner module to enable manually. Device support is firmware-dependent, so enabling the symbol does not guarantee runtime success.

## Test Signals

Useful checks include `make olddefconfig` and build tests for `DVB_USB_V2=m/y`, each child driver as module and built-in, `MEDIA_SUBDRV_AUTOSELECT` both enabled and disabled, and RC support enabled/disabled where allowed. Runtime smoke testing should confirm enabled USB IDs bind to expected modules and request expected firmware.
