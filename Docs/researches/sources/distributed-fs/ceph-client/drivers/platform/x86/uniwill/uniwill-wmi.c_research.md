# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/uniwill-wmi.c

Purpose: WMI event bridge for the Uniwill laptop driver. It listens for a known Uniwill-style event GUID and forwards integer event payloads to registered notifier blocks.

Important APIs and control flow: `devm_uniwill_wmi_register_notifier()` registers a notifier in `uniwill_wmi_chain_head` and arranges devm unregister. `uniwill_wmi_notify()` accepts only integer ACPI objects, logs the event value, and calls the blocking notifier chain. `uniwill_wmi_register_driver()` and `uniwill_wmi_unregister_driver()` are called manually by `uniwill-acpi.c`.

State and dependencies: global blocking notifier chain is the only persistent state. The WMI driver uses GUID `ABBC0F72-8EA1-11D1-00A0-C90629100000`, `min_event_size = sizeof(u32)`, and `no_singleton = true`.

Risks and test signals: the GUID is intentionally not trusted for autoloading because it may be copied by unrelated firmware; manual DMI-gated registration limits false binding. Tests should cover integer and non-integer WMI events, notifier registration/unregistration lifetime, multiple WMI devices, and behavior when the WMI driver cannot register after the ACPI platform driver is registered.
