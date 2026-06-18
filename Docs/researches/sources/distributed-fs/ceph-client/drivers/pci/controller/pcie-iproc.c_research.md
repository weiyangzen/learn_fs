# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc.c

## Purpose

`pcie-iproc.c` is the common Broadcom iProc PCIe host-controller implementation used by BCMA and platform wrappers. It abstracts PAXB/PAXC register layouts, configuration-space access, reset/link bring-up, outbound and inbound address translation, MSI steering to GIC ITS or internal MSI, PHY lifecycle, controller quirks, and PCI host registration.

## Important APIs, Types, And Functions

- `enum iproc_pcie_reg` and per-type register tables define valid offsets for PAXB BCMA, PAXB, PAXB v2, PAXC, and PAXC v2.
- `iproc_pcie_rev_init()` selects register tables and capabilities based on `pcie->type`, including config-read quirks, APB error disable, outbound/inbound map tables, internal endpoint behavior, and MSI steering.
- `iproc_pcie_config_read32()` and `iproc_pcie_config_write32()` wrap generic config access with optional APB error suppression and custom iProc reads.
- `iproc_pcie_config_read()` handles PAXB/PAXC custom reads, RRS retry status, PAXC capability fixups, and rejection of unconfigured physical functions.
- `iproc_pcie_check_link()` validates PHY/data-link status, verifies RC bridge mode, fixes class code, and retries Gen1 if a Gen2 link does not become active.
- `iproc_pcie_setup_ob()`, `iproc_pcie_map_ranges()`, `iproc_pcie_setup_ib()`, and `iproc_pcie_map_dma_ranges()` program outbound OARR/OMAP and inbound IARR/IMAP windows.
- `iproc_pcie_msi_enable()` resolves MSI nodes, performs optional MSI steering, and calls `iproc_msi_init()` for internal MSI when applicable.
- `iproc_pcie_setup()` is the exported setup entry point used by wrappers. It initializes revision state, PHY, PERST, address mappings, link, INTx, MSI, host bridge ops, scans the bus, and prints link status.
- `iproc_pcie_remove()` and `iproc_pcie_shutdown()` are exported lifecycle functions.

## Control Flow

Setup begins by selecting the register map and quirks. The PHY is initialized and powered, PERST is asserted and deasserted unless the endpoint is internal, and stale address mappings are invalidated. Optional outbound mappings are programmed from host bridge windows; optional inbound mappings are programmed from `dma_ranges`. Link checks are skipped for internal PAXC endpoints but otherwise verify hardware link bits and RC mode, force bridge class code, and possibly downshift to Gen1. The driver enables INTx, attempts MSI setup when `CONFIG_PCI_MSI` is enabled, installs `iproc_pcie_ops` on the host bridge, and scans. Remove stops and removes the root bus, disables MSI, powers off PHY, and exits PHY.

Config access uses an indirect address/data pair for RC config and endpoint config. For PAXB v2 reads, `iproc_pcie_cfg_retry()` handles hardware returning `0xffff0001` for RRS completions by polling config-read status. PAXC capability-list fixups alter returned config data for corrupted capability lists and hide unsupported RRS visibility.

## State And Persistence

`struct iproc_pcie` persists selected register offsets, mapping requirements, flags, and MSI pointer. Outbound/inbound mapping register state is invalidated and rebuilt at setup. `fix_paxc_cap` is latched after reading a known-bad device ID. MSI steering config persists in hardware until disabled or reset. No file-system persistence is used.

## Dependencies And Integration Points

The file integrates with PCI host bridge APIs, generic ECAM/config helpers, PHY framework, OF MSI translation, GICv3 ITS register definitions, irq/MSI support through `pcie-iproc-msi.c`, PCI fixup hooks, and wrapper-provided resources from BCMA or platform drivers. It exports setup/remove/shutdown symbols used by `pcie-iproc-bcma.c` and `pcie-iproc-platform.c`.

## Risks And Edge Cases

- `iproc_pcie_cfg_retry()` documents an ambiguity where real config data equal to `0xffff0001` can be mistaken for RRS retry status.
- Outbound mapping requires alignment and sufficient window sizes; the fallback minimum-window case can map more than the original resource.
- Inbound mapping must exactly match supported region sizes and alignments; malformed `dma-ranges` fail setup.
- PAXC unconfigured PF rejection relies on stale device ID `0x168e`; different firmware artifacts may escape rejection.
- MSI steering only supports GICv3 ITS and has separate PAXB v2 and PAXC v2 programming paths.
- Internal endpoints skip link and PERST handling, so behavior depends heavily on firmware pre-initialization.

## Test Signals

Run probe through both wrappers for every `iproc_pcie_type`, enumerate downstream devices, validate bridge class and link status, test RRS config retry and reads of `0xffff0001`, verify outbound/inbound mapping with aligned and unaligned resources, exercise internal PAXC PF rejection, check GIC ITS MSI steering and internal MSI fallback, test removal/shutdown PERST behavior, and verify PCI fixups for listed Broadcom device IDs.
