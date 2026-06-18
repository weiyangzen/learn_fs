# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.h

Purpose: shared event-code and notifier API header for Uniwill WMI hotkey events. It names OSD/event constants used by the WMI bridge and ACPI driver.

Important APIs and types: defines event IDs for lock keys, touchpad, radio, webcam, brightness, lightbar, fan, battery, USB/DC adapter, performance mode, keyboard illumination, mic mute, fn lock, and other OEM notifications. Declares `devm_uniwill_wmi_register_notifier()`, `uniwill_wmi_register_driver()`, and `uniwill_wmi_unregister_driver()`.

State and dependencies: no state. The header depends on init annotations and forward declarations for `struct device` and `struct notifier_block`.

Risks and test signals: event-code meanings are firmware ABI and some are ignored or uncertain in the consumer. Tests should verify keymap mappings in `uniwill-acpi.c` stay aligned with these constants and that new constants do not collide.
