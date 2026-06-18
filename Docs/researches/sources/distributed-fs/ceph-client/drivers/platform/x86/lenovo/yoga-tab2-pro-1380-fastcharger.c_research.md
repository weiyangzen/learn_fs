<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c

## Purpose
This driver implements the custom fast-charging handshake for Lenovo Yoga Tablet 2 Pro 1380F/1380L. It creates a serdev device on UART3, sends a charger command, then switches USB data lines to GPIO-high mode so the original charger can move from 5V to 12V.

## Important APIs, Types, And Functions
`struct yt2_1380_fc` stores pinctrl states, GPIOs, extcon, notifier, work item, and device pointer. `yt2_1380_fc_worker()` performs the retry handshake. `yt2_1380_fc_extcon_evt()` schedules work on charger state changes. `yt2_1380_fc_serdev_probe()` initializes extcon, pinctrl, GPIOs, serdev baud rate, and extcon notifier. `yt2_1380_fc_pdev_probe()` registers pinctrl mappings, locates the `PNP0501` serial controller, creates a serdev child, and manually attaches the serdev driver.

## Control Flow
Module init registers the serdev driver before the platform driver because platform probe creates and attaches the serdev. The worker exits if already fast charging, otherwise retries up to five times: select UART mode, confirm DCP charger, write `"SC"` at 600 baud, wait, confirm charger still connected, select GPIO mode, wait for voltage switch, and check `EXTCON_CHG_USB_FAST`. Failure restores UART mode.

## State And Persistence
The driver has no persistent policy state; it reacts to extcon state and pinctrl mode. GPIO line mode is actively changed between UART and output-high GPIO during the protocol.

## Dependencies And Integration Points
It depends on extcon state from `i2c-lc824206xa`, serdev helpers, pinctrl mappings for `INT33FC:00`, GPIO descriptors propagated through fwnode from x86-android-tablets, and platform alias `lenovo-yoga-tab2-pro-1380-fastcharger`.

## Risks And Edge Cases
The protocol is timing-sensitive and charger-specific. Work is scheduled from extcon notifications and initial probe; removal does not explicitly cancel work in this file, relying on device lifecycle ordering. Manual serdev attachment maps `-EAGAIN` back to `-EPROBE_DEFER`. Incorrect pinctrl/GPIO definitions could drive USB data lines incorrectly.

## Test Signals
Validation needs original and non-original chargers, DCP-only and fast-charger extcon transitions, retry/failure logging, pinctrl mode switching, UART write length, probe deferral for extcon/serial controller, and removal while work may be pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c -->
