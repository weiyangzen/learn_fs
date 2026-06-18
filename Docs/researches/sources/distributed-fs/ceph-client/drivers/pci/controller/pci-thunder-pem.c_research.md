# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-pem.c

## Purpose
`pci-thunder-pem.c` supports Cavium Thunder PEM PCIe root bridges, where the root bridge itself uses a PEM-specific indirect config access mechanism while devices behind it use ECAM. It also synthesizes fixed MSI-X/EA capability information and supports both OF and ACPI firmware descriptions, including legacy ACPI resource reconstruction.

## Important APIs, Types, And Functions
`struct thunder_pem_pci` stores synthesized EA entry dwords and the PEM register base. `thunder_pem_bridge_read()` and `thunder_pem_bridge_write()` implement indirect 32-bit config cycles via `PEM_CFG_RD` and `PEM_CFG_WR`. `thunder_pem_config_read()` / `thunder_pem_config_write()` route bus-start/devfn0 accesses to the bridge helpers and all other accesses to generic ECAM. `thunder_pem_init()` maps the PEM register space and constructs EA data for the fixed MSI-X BAR. `thunder_pem_ecam_ops` is the ACPI-facing ops object; `pci_thunder_pem_ops` is used by the OF platform driver.

## Control Flow, State, And Persistence
Initialization maps the PEM register block and stores `struct thunder_pem_pci` in `cfg->priv`. Reads of bridge config space trigger an indirect read, then patch capability pointers, PME vector, MSI-X table/PBA offsets, EA header, and EA entry dwords. Writes smaller than dword are expanded by read-modify-write; W1C bits are masked to avoid accidental clearing, and selected fields are forced to one to emulate read-only behavior. No persistent disk state exists; runtime state is the mapped PEM base plus EA values derived from the PEM resource start/end.

## Dependencies, Integration Points, Risks, And Test Signals
The driver integrates with `pci-host-common`, generic ECAM, ACPI PCI root helpers, OF resources, `request_mem_region()` for legacy reservation, and Cavium-specific ACPI resource lookup via `"CAVA02B"`. It uses a non-standard ECAM bus shift of 24. Risks are incorrect root segment/node/index reconstruction for legacy ACPI firmware, accidental W1C status clearing during sub-dword writes, and capability synthesis mismatches between variants. Test root bridge enumeration, byte/word config writes, valid MSI-X/EA layout, ACPI reservation behavior, and normal downstream ECAM access.
