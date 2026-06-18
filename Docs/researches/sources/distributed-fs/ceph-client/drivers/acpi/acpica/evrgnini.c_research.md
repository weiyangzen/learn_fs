# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evrgnini.c

## Purpose
Provides address-space-specific setup routines for operation regions and the region initialization search that binds newly created regions to the nearest installed handler. It creates and destroys per-region contexts for memory, IO, PCI config, data table, and default spaces, detects PCI root bridges, and runs `_REG(CONNECT)` after successful handler attachment.

## Important APIs, Types, And Functions
- `acpi_ev_system_memory_region_setup` creates `acpi_mem_space_context` and frees all cached memory mappings on deactivate.
- `acpi_ev_io_space_region_setup`, `acpi_ev_default_region_setup`, `acpi_ev_pci_bar_region_setup`, and `acpi_ev_cmos_region_setup` provide simple or placeholder setup behavior.
- `acpi_ev_pci_config_region_setup` discovers PCI segment/bus/device/function, installs a handler on a PCI root bridge when only the root default handler is present, and returns an `acpi_pci_id` context.
- `acpi_ev_is_pci_root_bridge` detects PCI/PCIe root bridges via `_HID` and `_CID`.
- `acpi_ev_data_table_region_setup` creates/frees an `acpi_data_table_mapping`.
- `acpi_ev_initialize_region` searches upward from the region's parent for a matching handler, attaches the region, exits the interpreter, and runs `_REG(CONNECT)`.

## Control Flow
Setup callbacks receive activate/deactivate function codes. Memory deactivate unmaps every cached mapping and frees context; activate records region address/length. IO and default setup reuse handler context. PCI config setup handles deactivation by freeing existing PCI ID, then on activation identifies the PCI root bridge, possibly installs a more specific default handler, evaluates `_ADR`, `_SEG`, and `_BBN`, derives the full PCI ID, and returns it. Region initialization marks the object initialized once, walks parent scopes toward root, inspects handlers on devices/processors/thermal/root, attaches the first matching handler, and notifies firmware with `_REG(CONNECT)`.

## State And Persistence
Per-region contexts persist in the region secondary object's `extra.region_context`. Memory contexts own a mapping list; PCI contexts own derived bus identity; data-table contexts hold a table pointer. Region objects persist initialization flags, handler attachment, node pointers, space ID, address, and length.

## Dependencies And Integration Points
Depends on operation-region dispatch and handler registration, namespace attached objects, PCI helper evaluation and derivation, ACPI `_HID`/`_CID`/`_ADR`/`_SEG`/`_BBN` execution helpers, OS memory unmapping, and interpreter lock management around `_REG`.

## Risks And Edge Cases
PCI config setup may be called while a root default handler is still attached and must re-associate to the nearest PCI root bridge without losing context creation. Missing `_ADR`, `_SEG`, or `_BBN` default to zero where permitted, but no enclosing device is an operand error. Memory deactivate must clear all mappings to avoid stale virtual addresses. `AOPOBJ_OBJECT_INITIALIZED` is set before handler discovery, so later handler installation paths must attach regions independently.

## Test Signals
Signals include memory mapping cleanup on deactivate, IO/default context passthrough, PCI root bridge detection by HID and CID, PCI ID derivation from `_ADR`/`_SEG`/`_BBN`, handler search from region parent to root, `_REG(CONNECT)` after attach, no-handler initialization succeeding without attachment, and data table mapping allocation/free.
