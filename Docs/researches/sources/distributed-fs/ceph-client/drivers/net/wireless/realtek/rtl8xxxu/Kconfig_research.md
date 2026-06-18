# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Kconfig

## Purpose

This Kconfig file exposes build-time configuration for the `rtl8xxxu` Realtek 802.11n USB wireless driver. It defines the main `RTL8XXXU` tristate option and a subordinate `RTL8XXXU_UNTESTED` boolean that expands device detection to untested Realtek USB IDs.

## Important Symbols

- `config RTL8XXXU`: enables built-in or module compilation of the mac80211-based Realtek RTL8XXX USB driver. The resulting module name is `rtl8xxxu`.
- `depends on MAC80211 && USB`: requires the mac80211 stack and USB support.
- `depends on LEDS_CLASS`: requires LED class support because the driver exposes LED class device behavior through fileops such as the RTL8723BU brightness setter.
- `config RTL8XXXU_UNTESTED`: optional experimental detection path for untested 8723/8188/8191/8192 WiFi USB devices.
- `depends on RTL8XXXU`: the untested-device switch is only visible when the base driver is enabled.

## Control Flow and Build Behavior

Kconfig does not execute runtime logic. Its control effect is at kernel configuration time:

1. If `RTL8XXXU=n`, the driver objects listed in the Makefile are not built and no rtl8xxxu USB IDs are registered.
2. If `RTL8XXXU=m`, the objects are linked into `rtl8xxxu.ko`.
3. If `RTL8XXXU=y`, the same driver is built into the kernel image.
4. If `RTL8XXXU_UNTESTED=y`, `core.c` compiles additional USB ID table entries guarded by `CONFIG_RTL8XXXU_UNTESTED`, increasing hardware match coverage.

## State and Persistence Behavior

The selected values are stored in the generated kernel `.config` and propagated as preprocessor/build variables. They do not create runtime persistence by themselves, but they determine whether the driver is present and whether experimental IDs are compiled in.

## Dependencies and Integration Points

- Integrates with the kernel Kconfig system under the wireless Realtek driver tree.
- Feeds `CONFIG_RTL8XXXU` into the local Makefile so `rtl8xxxu.o` is produced.
- Feeds `CONFIG_RTL8XXXU_UNTESTED` into source conditionals, notably the USB device ID list in `core.c` and chip files with untested-specific ID guards.
- The help text documents coexistence with the older `rtlwifi` driver; operational module binding may still need user control if multiple drivers can match related hardware.

## Risks and Edge Cases

- `LEDS_CLASS` is a hard dependency. Minimal configurations without LED class support cannot build this driver even if LED functionality is not operationally important for a target board.
- Enabling `RTL8XXXU_UNTESTED` can make the driver bind to hardware whose register sequences, efuse layout, or RF frontend have not been validated, increasing probe or runtime regression risk.
- The help text says the driver lacks 40 MHz channel and power-management support. Users enabling it should not infer feature parity with vendor drivers.
- Coexistence with `rtlwifi` is possible but not automatic policy. Module alias ordering, blacklists, or manual binding may be needed to choose one driver.
- The help text has historical chip-list wording and should be kept aligned with actual USB IDs and fileops support when chips are added or removed.

## Test Signals

- Run Kconfig dependency checks through a kernel build configuration with `RTL8XXXU=m` and verify `rtl8xxxu.ko` is produced.
- Verify that disabling `MAC80211`, `USB`, or `LEDS_CLASS` hides or prevents the base option as expected.
- Compare USB device alias output with `RTL8XXXU_UNTESTED=n` and `y` to confirm experimental IDs are gated.
- Smoke-test module loading on systems where `rtlwifi` could also bind and confirm the expected module owns the USB interface.
