# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/pcie_quirks.h

Purpose: Declares the PCIe quirk interface shared between `pcie.c` and `pcie_quirks.c`.

Important APIs and types: Defines `QUIRK_FW_RST_D3COLD` as bit 0 and declares `mwifiex_initialize_quirks(struct pcie_service_card *card)` plus `mwifiex_pcie_reset_d3cold_quirk(struct pci_dev *pdev)`. It includes `pcie.h`, so consumers receive both the PCI device type and `struct pcie_service_card`.

Control flow and state behavior: The header itself is declarative. The quirk bit is stored in `pcie_service_card.quirks` and later tested by reset code. A single bitmask leaves space for future independent platform quirks without changing the card structure.

Dependencies and integration points: Tightly coupled to the mwifiex PCIe backend; not a general quirk registry. It depends on Linux `BIT()` availability through included headers and on PCI declarations imported by `pcie.h`.

Risks and test signals: Since `QUIRK_FW_RST_D3COLD` is a public bit between two C files, new quirk bits must avoid collisions and callers must test bits rather than compare exact masks. Compile tests should include this header from both implementation files, and reset tests should verify behavior when no quirk bits are set.
