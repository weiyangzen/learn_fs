# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Kconfig

## Purpose
This Kconfig file defines the configurable build surface for DVB frontend drivers when `MEDIA_DIGITAL_TV_SUPPORT` is enabled. It organizes demodulators, tuners, SEC controllers, Common Interface devices, and test-only frontends into the `Customise DVB Frontends` menu, while allowing ancillary subdrivers to be hidden by `MEDIA_HIDE_ANCILLARY_SUBDRV`.

## Important APIs, Types, And Build Contracts
The file exports Kconfig symbols rather than C APIs. For this work item, the important symbols are `DVB_A8293`, `DVB_AF9013`, `DVB_AF9033`, `DVB_AS102_FE`, `DVB_ASCOT2E`, `DVB_ATBM8830`, `DVB_AU8522`, `DVB_AU8522_DTV`, and `DVB_AU8522_V4L`. Most visible frontend symbols are `tristate` and default to module builds when `MEDIA_SUBDRV_AUTOSELECT` is disabled. Dependencies express runtime subsystem requirements, typically `DVB_CORE && I2C`, with extra requirements such as `I2C_MUX` for AF9013 and `VIDEO_DEV` for AU8522 analog/V4L support. `DVB_AF9013` selects `REGMAP`; `DVB_AF9033` selects `REGMAP_I2C`; AU8522 DTV and V4L variants select the hidden common `DVB_AU8522`.

## Control Flow And Integration
Kconfig does not execute device logic, but it drives compilation and module availability. `DVB_AS102_FE` is hidden and defaults to `DVB_AS102`, so the USB/device parent selects the frontend automatically. AU8522 splits common support from DTV and analog decoder modules: `DVB_AU8522_DTV` and `DVB_AU8522_V4L` select common state/register helpers. The file also sources nested Kconfig files for subdirectories such as `cxd2880` and `drx39xyj`.

## State, Persistence, And Dependencies
Configuration state persists in the kernel build `.config`. Build-time dependencies protect against missing I2C, DVB core, regmap, I2C mux, or V4L2 infrastructure. There is no runtime persistence.

## Risks
Incorrect dependencies can build drivers without required helper subsystems or hide attach stubs unexpectedly. The AU8522 split is especially sensitive: common helpers must be present when either DTV or V4L modules are enabled. `DVB_AF9033` advertises many clocks in its public header, but the implementation in this tree currently rejects clocks other than 12 MHz at probe, so Kconfig alone does not describe all runtime constraints.

## Test Signals
Useful validation is configuration matrix testing: `allyesconfig`, `allmodconfig`, and targeted module builds for each symbol. Probe-path tests need matching hardware or emulated I2C/regmap coverage; Kconfig validation should confirm selected dependencies appear in generated `.config`.
