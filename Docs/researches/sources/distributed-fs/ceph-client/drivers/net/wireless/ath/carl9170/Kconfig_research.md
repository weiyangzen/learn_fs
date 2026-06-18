# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Kconfig

## Purpose
`Kconfig` defines build-time configuration for the carl9170 USB 802.11n driver and optional features. It exposes the main driver, LED support, debugfs, WPS push-button input support, and hardware RNG support.

## Important APIs, types, and options
`CONFIG_CARL9170` is a tristate depending on `USB` and `MAC80211`, selecting `ATH_COMMON`, `FW_LOADER`, and `CRC32`. `CONFIG_CARL9170_LEDS` defaults to enabled when mac80211 LED support exists. `CONFIG_CARL9170_DEBUGFS` depends on debugfs and mac80211 debugfs and defaults off. `CONFIG_CARL9170_WPC` is an internal bool tied to input support. `CONFIG_CARL9170_HWRNG` optionally exposes the firmware/device RNG with a transport eavesdropping warning.

## Control flow and integration
There is no runtime control flow. These symbols drive conditional compilation in the Makefile and driver headers, selecting optional fields and objects such as debugfs and LED code. The main help text documents the required `carl9170-1.fw` firmware.

## State and persistence behavior
State is build configuration only. Choices persist in the kernel `.config` and determine which code and struct fields exist in the built module.

## Dependencies
The configuration depends on kernel USB, mac80211, debugfs, LED, input, firmware loader, CRC32, and hwrng subsystems.

## Risks
Risks include enabling `CARL9170_HWRNG` without accepting USB transport observability, building the driver without required firmware availability, and optional feature dependencies changing struct layout or code paths. Debugfs defaults off, which can surprise diagnostics users.

## Test signals
Signals include Kconfig dependency resolution for built-in and module builds, module name `carl9170`, firmware request behavior, LED/debugfs/HWRNG symbols compiling in all valid combinations, and no unresolved references when optional subsystems are disabled.
