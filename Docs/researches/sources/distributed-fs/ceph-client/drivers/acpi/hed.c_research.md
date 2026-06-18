# sources/distributed-fs/ceph-client/drivers/acpi/hed.c

Purpose: `hed.c` implements the ACPI Hardware Error Device driver for `PNP0C33`. It receives ACPI device notifications used for hardware error signaling and forwards them to registered HED notifier clients, mainly for SCI-notified HEST Generic Hardware Error Sources.

Important APIs, types, and functions: exported APIs are `register_acpi_hed_notifier()` and `unregister_acpi_hed_notifier()`. Core functions are `acpi_hed_notify()`, `acpi_hed_probe()`, and `acpi_hed_remove()`. `hed_handle` enforces a single HED instance.

Control flow: subsystem init registers a platform driver matched on `PNP0C33`. Probe obtains the ACPI companion, rejects additional HED instances, records the handle, and installs an ACPI device notify handler. When firmware notifies the device, the handler calls the blocking notifier chain. Remove unregisters the ACPI notify handler and clears the global handle.

State and persistence: state consists of the single global `hed_handle` and the blocking notifier chain. No event payload is persisted; notifications simply wake registered clients.

Dependencies and integration: integrates ACPI platform-device probing, ACPI notify handlers, Linux blocking notifiers, and external HED users declared through `<acpi/hed.h>`.

Risks: only one HED is supported; systems exposing multiple matching devices will reject later probes. The notifier has no event details, so consumers must discover error state elsewhere. Blocking notifier callbacks can delay notification processing.

Test signals: verify single-instance enforcement, notify handler install/remove, notifier registration and callback delivery, remove cleanup, and behavior when no ACPI companion exists.
