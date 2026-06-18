# sources/distributed-fs/ceph-client/include/linux/surface_acpi_notify.h

Purpose: declares the Surface ACPI Notify client interface for receiving discrete-GPU ACPI events produced by the SAN driver.

Important APIs and types: `struct san_dgpu_event` carries category, target, command, instance, payload length, and payload pointer. APIs are `san_client_link()`, `san_dgpu_notifier_register()`, and `san_dgpu_notifier_unregister()`.

Control flow: a client links itself to the SAN provider device, registers a notifier block for dGPU events, receives event payloads via the notifier chain, and unregisters before teardown.

State and persistence: event data is transient; notifier registration state lives in the SAN driver and notifier chain. No persistent state is defined here.

Dependencies and integration points: depends on notifier blocks, device objects, and integer types. It integrates Microsoft Surface platform drivers that need SAN-mediated dGPU notifications.

Risks and test signals: risks include notifier lifetime races, payload pointer lifetime misuse, unregister ordering during device removal, and malformed ACPI event lengths. Test with Surface dGPU hotplug/power events, driver unload, ACPI notification storms, and bounds checks on payload consumers.
