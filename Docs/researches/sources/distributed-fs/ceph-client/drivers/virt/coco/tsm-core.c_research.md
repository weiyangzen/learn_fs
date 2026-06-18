# sources/distributed-fs/ceph-client/drivers/virt/coco/tsm-core.c

## Purpose
Implements a generic TEE Security Manager device class and registration API, with optional PCI TSM integration.

## APIs, Types, and Functions
Exports `tsm_register()`, `tsm_unregister()`, and `find_tsm_dev()`. Internal helpers are `alloc_tsm_dev()`, `tsm_register_pci_or_reset()`, `match_id()`, and `tsm_release()`. Global state is `tsm_class` and `tsm_ida`.

## Control Flow and State
Module init registers class `tsm`. Registration allocates a `struct tsm_dev`, allocates an ID, initializes an embedded `struct device`, names it `tsm%d`, adds it to the class, optionally registers PCI TSM ops, and emits a `KOBJ_CHANGE` uevent when PCI TSM becomes available. Unregistration reverses PCI TSM registration if present and unregisters the device; release frees the ID and memory.

## Dependencies and Integration
Depends on Linux device classes, IDA, cleanup annotations, and `pci_tsm_register()/pci_tsm_unregister()`.

## Risks and Test Signals
Risks include reference lifetime through `find_tsm_dev()`, PCI registration failure after device add, and uevent ordering. Tests should cover register/unregister cycles, failed `dev_set_name()`/`device_add()`, PCI ops failure rollback, ID reuse, and class unregister after devices are gone.
