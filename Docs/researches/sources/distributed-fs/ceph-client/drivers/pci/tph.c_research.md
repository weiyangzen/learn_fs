# sources/distributed-fs/ceph-client/drivers/pci/tph.c

## Purpose
`tph.c` implements PCIe TLP Processing Hints support. It discovers requester capability, enables and disables TPH modes, manages Steering Tag table entries in either TPH capability space or MSI-X tables, queries ACPI firmware for CPU-local steering tags, and saves/restores TPH state across device power transitions.

## Important APIs, types, and functions
Key exported APIs are `pcie_tph_get_st_table_loc()`, `pcie_tph_get_st_table_size()`, `pcie_tph_get_cpu_st()`, `pcie_tph_set_st_entry()`, `pcie_disable_tph()`, and `pcie_enable_tph()`. PCI core hooks include `pci_restore_tph_state()`, `pci_save_tph_state()`, `pci_no_tph()`, and `pci_tph_init()`. Under ACPI, `union st_info`, `tph_invoke_dsm()`, and `tph_extract_tag()` parse the PCI firmware DSM result.

## Control flow and behavior
Initialization finds the TPH extended capability and allocates a save buffer sized for the control register plus any in-capability ST table entries. Enabling rejects global `notph`, missing capability, duplicate enable, unsupported ST modes, or missing requester/completer support. It chooses 8-bit or extended TPH request type based on device capability and root-port completer support, writes mode and requester-enable fields, and records `pdev->tph_enabled`, `tph_mode`, and `tph_req_type`.

Setting an ST entry requires TPH enabled. It disables requester TPH while updating, writes either the MSI-X TPH tag or capability-table word, disables TPH on write failure, then restores requester enable. ACPI CPU tag lookup maps a Linux CPU to ACPI UID, invokes the root-port DSM, and extracts volatile or persistent-memory steering tags matching the negotiated request type. Save/restore copy the control register and ST entries to or from the PCI saved-capability buffer.

## State and persistence
Persistent state is in `struct pci_dev` fields `tph_cap`, `tph_enabled`, `tph_mode`, and `tph_req_type`, plus saved extended capability data. Hardware state lives in TPH capability control and ST table fields or MSI-X ST storage. `pci_tph_disabled` is a process-wide boot/runtime switch set by `pci_no_tph()`.

## Dependencies and integration points
The file depends on PCIe extended capabilities, root-port discovery, MSI-X TPH tag helpers, ACPI DSM support, ACPI CPU UID mapping, saved capability buffers, and `pci_add_ext_cap_save_buffer()`.

## Risks
The DSM buffer is interpreted as a 64-bit structure and depends on firmware conformance. ST table index bounds only apply to capability-resident tables; MSI-X table errors are delegated. Updating ST entries requires temporarily disabling TPH to avoid device instability. Request-type negotiation must not enable extended TPH unless both requester and completer support it.

## Test signals
Test devices with no TPH, each ST mode, MSI-X and capability ST tables, invalid ST indices, root ports with reduced completer support, ACPI DSM success/failure, `notph`, suspend/resume save-restore, and write failure rollback that disables TPH.
