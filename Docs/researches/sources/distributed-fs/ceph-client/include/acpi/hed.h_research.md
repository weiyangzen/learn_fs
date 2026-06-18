# sources/distributed-fs/ceph-client/include/acpi/hed.h

Purpose: Declares the ACPI Hardware Error Device notifier API used by APEI/GHES and other firmware-first error consumers.

Important APIs, types, and functions: Exports `register_acpi_hed_notifier()` and `unregister_acpi_hed_notifier()` for `struct notifier_block`.

Control flow: Clients register notifier blocks; HED event handling invokes them when ACPI hardware error notifications arrive.

State and persistence: Notifier-chain state is owned by the HED implementation. No persistent data is represented here.

Dependencies and integration points: Depends on Linux notifier API. Integrates with GHES, ACPI error devices, and platform RAS reporting.

Risks and test signals: Risks are notifier ordering/lifetime bugs and missing unregister during module/device teardown. Test notifier registration failures, event delivery, unregister races, and ACPI HED absent builds.
