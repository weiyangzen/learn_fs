# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-hisi-error.c

## Purpose

`pcie-hisi-error.c` is an ACPI/APEI GHES vendor-record handler for HiSilicon HIP PCIe controller errors. It recognizes a HiSilicon-specific CPER section GUID, decodes controller error payload fields, logs valid metadata and miscellaneous registers, and attempts recovery for recoverable errors by removing and rescanning the affected root port after invoking an ACPI reset method.

## Important APIs, Types, And Functions

- `struct hisi_pcie_error_data` models the vendor CPER payload: validity bitmap, topology identifiers, submodule, severity/type, and 33 miscellaneous registers.
- `struct hisi_pcie_error_private` stores the GHES notifier and owning device.
- `hisi_pcie_notify_error()` is the GHES notifier callback. It filters by section GUID and ACPI device `socket` property before handling the payload.
- `hisi_pcie_handle_error()` logs all valid fields and misc registers, then triggers recovery only when severity is `HISI_PCIE_ERR_SEV_RECOVERABLE`.
- `hisi_pcie_port_do_recovery()` locates the ACPI PCI root, gets the root port `pci_dev`, removes it under PCI locking, calls the reset method, waits one second, and rescans the root bus.
- `hisi_pcie_port_reset()` evaluates ACPI method `RST` with socket/chip, core ID, and core port ID arguments derived from firmware port identifiers.
- `hisi_pcie_error_handler_probe()` allocates private state and registers the vendor-record notifier with `devm_ghes_register_vendor_record_notifier()`.

## Control Flow

The platform driver binds via ACPI ID `HISI0361`. Probe allocates private notifier state and registers with GHES. On each vendor CPER notification, the callback imports the section GUID, ignores records for other vendors, verifies the platform device socket property, and ignores records for other sockets. Matching records are decoded and logged. For recoverable severity, the code computes the PCI root-port devfn from core/port IDs, removes the root port and downstream devices, calls ACPI `RST`, waits for subordinate device initialization time, and rescans the ACPI root bus.

## State And Persistence

There is almost no persistent driver state beyond the registered notifier and device pointer. Recovery intentionally changes PCI core state by hot-removing and rescanning devices under the affected root port. Error information is consumed from the GHES-provided buffer; it is not stored after logging. The ACPI firmware owns reset semantics and persistent platform topology.

## Dependencies And Integration Points

The driver depends on ACPI GHES vendor-record notification, `acpi_hest_get_payload()`, ACPI root lookup (`acpi_pci_find_root()`), PCI core hot-remove/rescan helpers, ACPI method `RST`, and a device property named `socket`. It integrates with platform-driver matching through ACPI table `HISI0361`.

## Risks And Edge Cases

- Payload validation is based on `val_bits`, but recovery still uses `socket_id`, `core_id`, and `port_id` fields for recoverable errors; malformed firmware records could target the wrong root port.
- `pci_stop_and_remove_bus_device_locked()` disrupts all downstream devices. Driver correctness depends on re-enumeration and endpoint driver recovery.
- The one-second wait is conservative but fixed; endpoints with unusual readiness behavior may still fail rescan.
- If ACPI `RST` is absent or returns failure, recovery stops after the root port was removed, leaving recovery to later rescans or manual intervention.
- The notifier ignores records without a matching `socket` property, so platform firmware and ACPI device properties must agree.

## Test Signals

Test by injecting or replaying GHES records with the HiSilicon GUID, verifying nonmatching GUIDs and sockets return `NOTIFY_DONE`, checking decoded log output for each valid bit, confirming recoverable errors remove and rescan only the targeted root port, testing missing/failing ACPI `RST`, and ensuring fatal/corrected/none severities log without hot-remove recovery.
