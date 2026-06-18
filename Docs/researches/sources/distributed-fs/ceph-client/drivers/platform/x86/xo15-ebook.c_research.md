# sources/distributed-fs/ceph-client/drivers/platform/x86/xo15-ebook.c

Purpose: ACPI input driver for the OLPC XO-1.5 ebook/tablet-mode switch. It reports the firmware `EBK` method state as `SW_TABLET_MODE`.

Important APIs/types/functions: `ebook_device_ids` matches ACPI HID `XO15EBK`. `struct ebook_switch` stores the input device and physical path string. `ebook_send_state()` evaluates ACPI method `EBK` and reports `SW_TABLET_MODE` as the inverse of the returned state. `ebook_switch_notify()` handles ACPI fixed hardware and status notifications. `ebook_switch_add()` allocates/registers the input device and enables wakeup GPE if valid; `ebook_switch_remove()` unregisters it.

Control flow: ACPI add allocates state, matches the HID, sets ACPI device name/class, configures an input device with EV_SW/SW_TABLET_MODE, registers it, immediately sends current state, and enables wakeup if firmware marks the GPE as valid. Notifications and resume both call `ebook_send_state()` to refresh userspace-visible switch state.

State and persistence: runtime state is the allocated input device and path string. The authoritative switch state remains in ACPI firmware. Wakeup enable state is configured through ACPI/device PM and persists until device removal or system power change.

Dependencies/integration: uses ACPI driver framework, ACPI method evaluation, input subsystem switch events, PM sleep resume hook, and ACPI wakeup GPE handling.

Risks: `EBK` failure returns `-EIO` and prevents state update. The driver inverts firmware state, so semantic regressions are easy if firmware meaning is misread. Wakeup GPE is enabled directly when valid, so platforms with incorrect wake metadata may see unwanted wake behavior.

Test signals: initial state should match physical ebook/tablet mode, ACPI notification `0x80` should update `SW_TABLET_MODE`, resume should resend state, unsupported notification types should only debug-log, and wake from ebook switch should work when firmware exposes a valid wake GPE.
