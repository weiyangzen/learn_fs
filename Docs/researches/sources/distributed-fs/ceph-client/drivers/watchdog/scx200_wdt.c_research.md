# sources/distributed-fs/ceph-client/drivers/watchdog/scx200_wdt.c

## Purpose
`scx200_wdt.c` is a legacy NatSemi SCx200 watchdog driver exposing the chipset watchdog through the old misc `/dev/watchdog` interface. It programs the SCx200 configuration block watchdog registers directly with port I/O, supports magic close, configurable timeout, reboot notifier shutdown handling, and a single-open policy.

## Important APIs, types, and functions
The driver is built around module parameters `margin` and `nowayout`, global state `wdto_restart`, `expect_close`, `open_lock`, and `scx_lock`, and the miscdevice `scx200_wdt_miscdev`. Core hardware helpers are `scx200_wdt_ping()`, `scx200_wdt_update_margin()`, `scx200_wdt_enable()`, and `scx200_wdt_disable()`. User entry points are `scx200_wdt_open()`, `scx200_wdt_release()`, `scx200_wdt_write()`, and `scx200_wdt_ioctl()`, with `scx200_wdt_notify_sys()` disabling the timer on halt or poweroff when allowed.

## Control flow
Module init verifies `scx200_cb_present()`, reserves the SCx200 watchdog I/O slice, computes `wdto_restart = margin * W_SCALE`, disables the watchdog into a known state, registers a reboot notifier, then registers `/dev/watchdog`. Opening the device atomically claims `open_lock` and enables hardware by clearing WDTO/status, writing `W_ENABLE`, then pinging. Writes ping and scan for `V` to permit a later clean close. Ioctls report support/status, ping, and update timeout. Release disables only when magic close was seen and `nowayout` is false.

## State and persistence behavior
Persistent runtime state is in globals plus hardware registers under `scx200_cb_base`. No filesystem state exists. Hardware state persists across process close unless magic close is honored, and may persist across shutdown if `nowayout` is set. `open_lock` prevents concurrent users; `scx_lock` serializes port register sequences.

## Dependencies and integration points
The file depends on `<linux/scx200.h>` for configuration-block offsets and detection, direct `outb/outw` I/O, the misc watchdog minor, reboot notifiers, and watchdog ioctl constants. It predates the modern `watchdog_device` core and therefore implements the character-device behavior itself.

## Risks and test signals
Risks include unchecked large `margin` overflow into 16-bit `wdto_restart`, direct I/O to legacy registers, partial hardware changes before notifier or misc registration failures, and global `expect_close` semantics. Test signals are successful build on SCx200-enabled x86, correct rejection when the configuration block is absent or busy, single-open enforcement, `WDIOC_SETTIMEOUT` updating the reload value, magic-close behavior with and without `nowayout`, reboot-notifier disable on halt/poweroff, and observable WDTO reloads on real hardware.
