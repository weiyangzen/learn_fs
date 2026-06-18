# sources/distributed-fs/ceph-client/drivers/staging/greybus/Kconfig

## Purpose

`Kconfig` defines the Greybus staging driver configuration menu. It gates class drivers, bridged PHY drivers, audio support, firmware/bootrom support, and the Arche platform driver under the parent `GREYBUS` symbol.

## Important APIs, Types, and Functions

Important symbols include `GREYBUS_AUDIO`, `GREYBUS_AUDIO_APB_CODEC`, `GREYBUS_BOOTROM`, `GREYBUS_CAMERA`, `GREYBUS_FIRMWARE`, `GREYBUS_HID`, `GREYBUS_LIGHT`, `GREYBUS_LOG`, `GREYBUS_LOOPBACK`, `GREYBUS_POWER`, `GREYBUS_RAW`, `GREYBUS_VIBRATOR`, `GREYBUS_BRIDGED_PHY`, `GREYBUS_GPIO`, `GREYBUS_I2C`, `GREYBUS_PWM`, `GREYBUS_SDIO`, `GREYBUS_SPI`, `GREYBUS_UART`, `GREYBUS_USB`, and `GREYBUS_ARCHE`.

## Control Flow

The menu is active only when `GREYBUS` is enabled. `GREYBUS_BRIDGED_PHY` opens a nested block for bus-tunneling drivers. Individual symbols map to module objects in the Makefile.

## State and Persistence Behavior

There is no runtime state. Configuration choices persist in kernel `.config` and determine which objects are built-in or modules.

## Dependencies and Integration Points

Dependencies tie drivers to subsystems: audio depends on `SOUND` and `SND_SOC`, camera depends on media/flash LEDs and `BROKEN`, firmware and SPI bridge depend on SPI, HID depends on HID/input, power depends on `POWER_SUPPLY`, GPIO selects `GPIOLIB_IRQCHIP`, SDIO depends on MMC, UART depends on TTY, USB depends on USB, and Arche depends on `USB_HSIC_USB3613` or `COMPILE_TEST`.

## Risks and Edge Cases

Some help text appears stale: `GREYBUS_LOOPBACK` says it follows the debug log spec and module will be `gb-log.ko`. Camera is gated by `BROKEN`, making it intentionally unavailable in normal builds. Audio APBridge codec depends on both SND_SOC and `GREYBUS_AUDIO`, matching the split modules in the Makefile.

## Test Signals

Run allmodconfig/allyesconfig and targeted configs for audio, firmware, bootrom, each bridged PHY, and Arche. Confirm help text/module names, dependency propagation, and compile-test coverage.
