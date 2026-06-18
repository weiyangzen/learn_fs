# sources/distributed-fs/ceph-client/drivers/pci/vc.c

## Purpose
`vc.c` saves, restores, and re-enables PCIe Virtual Channel capabilities across reset and power-management transitions. It supports VC, VC9, and MFVC extended capabilities, including arbitration tables and per-resource control registers.

## Important APIs, types, and functions
Public PCI core hooks are `pci_save_vc_state()`, `pci_restore_vc_state()`, and `pci_allocate_vc_save_buffers()`. Internal helpers include `pci_vc_save_restore_dwords()`, `pci_vc_load_arb_table()`, `pci_vc_load_port_arb_table()`, `pci_vc_enable()`, and `pci_vc_do_save_buffer()`. The `vc_caps[]` table maps extended capability IDs to display names.

## Control flow and behavior
`pci_allocate_vc_save_buffers()` scans for MFVC, VC, and VC9 capabilities, asks `pci_vc_do_save_buffer()` for the exact serialized size, and allocates saved-capability buffers. Save and restore later repeat the scan and serialize or replay state in the same order.

`pci_vc_do_save_buffer()` reads capability metadata, saves/restores the port control register first, handles the VC arbitration table when low-priority VCs and an arbitration offset exist, then iterates each VC resource. For each resource it saves/restores optional port arbitration table data and the resource control register. On restore, it preserves any existing enable bit from FLR-surviving config, reloads arbitration tables when selected, and calls `pci_vc_enable()` when a VC must be re-enabled. `pci_vc_enable()` enables matching VC IDs on both downstream and upstream link ends when possible and waits for negotiation to finish.

## State and persistence
State is persisted in PCI saved extended capability buffers and restored to config space. Hardware state includes VC port control, VC arbitration tables, per-resource arbitration tables, resource control registers, and negotiation status bits.

## Dependencies and integration points
It depends on PCIe extended capability access, `pci_wait_for_pending()`, saved capability buffer management, downstream port detection, and upstream link matching through `dev->bus->self`.

## Risks
The buffer-size calculation must exactly match save/restore layout or restore returns `-ENOMEM`. Negotiation can remain pending and is only logged. Link-end matching by VC ID is best effort and skips root-bus or VC9 cases where the opposite endpoint is unavailable or unclear.

## Test signals
Test devices with VC, VC9, MFVC, multiple VC resources, arbitration table offsets and phase sizes, FLR followed by restore, missing upstream VC capability, stuck negotiation status, and saved-buffer size mismatches.
