<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c

## Purpose

This module is a central notifier source for ChromeOS USB Power Delivery events. It supports both ACPI notify delivery and Chrome EC platform-event delivery, fetches PD host-event status when possible, and broadcasts events through an exported blocking notifier chain.

## Important APIs, Types, And Functions

`cros_usbpd_register_notify()` and `cros_usbpd_unregister_notify()` are exported registration APIs. `struct cros_usbpd_notify_data` stores device, EC pointer, and optional EC notifier block. `cros_usbpd_get_event_and_notify()` sends `EC_CMD_PD_HOST_EVENT_STATUS` and calls the blocking notifier chain. ACPI probe installs an ACPI notify handler for `GOOG0003`; platform probe registers with `ecdev->ec_dev->event_notifier`.

## Control Flow

Module init registers the platform child driver and, under ACPI, a separate ACPI platform driver. ACPI notifies directly call the common fetch-and-broadcast helper. Platform EC notifications filter host events for PD MCU and USB mux bits before fetching PD status and broadcasting it. Removal unregisters the ACPI handler or EC notifier.

## State And Persistence

The notifier chain is static process-wide state. Per-device state holds the EC pointer and notifier block. There is no persistent event cache; events are broadcast when received, and late subscribers see only future events.

## Dependencies And Integration Points

The module integrates with Chrome EC event notifiers, ACPI notifications, Chrome EC PD host-event commands, and external consumers through `linux/platform_data/cros_usbpd_notify.h`. It recognizes ACPI IDs `GOOG0003` and parent `GOOG0004`.

## Risks

Older ACPI device hierarchies may lack an EC pointer; the driver intentionally broadcasts event 0 in that case, which consumers must handle. Probe deferral depends on detecting a `GOOG0004` parent. Blocking notifier callbacks run synchronously and can delay event handling.

## Test Signals

Test ACPI notify registration/removal, platform EC notifier registration/removal, event filtering, PD status command failures, parent EC probe deferral, exported notifier registration, and multiple subscriber behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c -->
