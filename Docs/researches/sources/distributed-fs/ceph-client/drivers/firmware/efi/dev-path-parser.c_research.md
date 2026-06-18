# sources/distributed-fs/ceph-client/drivers/firmware/efi/dev-path-parser.c

Purpose: maps EFI Device Path nodes to Linux `struct device` instances, currently supporting ACPI root nodes, PCI child nodes, and end-of-path markers.

Important APIs/types/functions: exports init-only `efi_get_device_by_path()`. Internal parsers are `parse_acpi_path()`, `parse_pci_path()`, `parse_end_path()`, and `match_pci_dev()`.

Control flow: `efi_get_device_by_path()` walks nodes while bytes remain. ACPI nodes validate length, derive an ACPI HID from EISA encoding, match UID, and return the first physical Linux device or the ACPI device itself. PCI nodes validate length and parent presence, then find a child PCI device by devfn. End nodes validate length/subtype, return the current parent, and either terminate the entire path or one instance. On each step the previous parent reference is dropped and the returned child becomes the new parent.

State and persistence behavior: no persistent state; returned devices have incremented references that callers must drop.

Dependencies and integration points: used by Apple property import and any EFI property/table consumer needing to bind firmware paths to Linux devices. Requires ACPI and PCI devices to exist, so callers should run no earlier than fs initcall level.

Risks and test signals: only a subset of EFI Device Path node types is implemented; unsupported paths return `-ENOTSUPP`. Pointer/length accounting must remain correct when updating `node` and `len`. Test signals include Apple property device matches on ACPI+PCI paths, correct reference balancing, and precise error offsets for malformed paths.
