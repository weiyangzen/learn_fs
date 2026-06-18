# sources/distributed-fs/ceph-client/drivers/pci/npem.c

## Purpose
Implements PCIe enclosure/status LED exposure for Native PCIe Enclosure Management and the ACPI `_DSM` PCIe SSD Status LED interface. It maps supported indication bits to Linux LED class devices so users can inspect and toggle enclosure indications.

## APIs, Types, And Functions
Main externally called functions are `pci_npem_create()` and `pci_npem_remove()`. Key types are `struct indication`, `struct npem_led`, `struct npem_ops`, `struct npem`, and `struct dsm_output`. Backend functions include direct NPEM config-space access (`npem_get_active_indications()`, `npem_set_active_indications()`) and ACPI DSM access (`dsm_evaluate()`, `dsm_get_active_indications()`, `dsm_set_active_indications()`).

## Control Flow
Creation prefers ACPI `_DSM` when all required LED functions exist, otherwise it probes the PCI NPEM extended capability and checks capability bits. Initialization filters supported indications, allocates one `npem_led` per supported bit, composes LED names, and registers LED class devices. LED `brightness_get` and `brightness_set` lazily initialize the active indication cache, serialize through a mutex, and either update NPEM control/status registers with command-completion polling or evaluate the `_DSM` set-state function.

## State And Persistence
`dev->npem` owns an allocated `struct npem` with backend ops, cached supported and active indication bitmasks, lazy initialization flag, mutex, capability offset, and flexible LED array. State is runtime-only but mirrors platform LED hardware/firmware state.

## Dependencies And Integration
Depends on PCI config-space access, ACPI DSM evaluation, LED class registration, mutexes, bit operations, and NPEM PCI register definitions. It integrates with PCI device create/remove paths that call `pci_npem_create()` and `pci_npem_remove()`.

## Risks And Test Signals
Risks include backend selection differences, lazy `_DSM` initialization failures before IPMI OpRegions are ready, stale active-indication cache, command-completion timeout, unsupported/reserved bit handling, LED unregister cleanup, and ACPI buffer validation. Test signals include platforms with native NPEM only, DSM-only platforms, partial DSM status code 4 handling, concurrent LED toggles, remove while LEDs are registered, and command timeout/error injection.
