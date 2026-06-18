# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.c

Purpose: Provides shared low-level R-Car PCIe helper functions used by host and endpoint code. It wraps MMIO reads/writes, byte-lane read/modify/write, PHY/data-link polling, and inbound/outbound address translation programming.

Important APIs/types/functions: Exports `rcar_pci_write_reg()`, `rcar_pci_read_reg()`, `rcar_rmw32()`, `rcar_pcie_wait_for_phyrdy()`, `rcar_pcie_wait_for_dl()`, `rcar_pcie_set_outbound()`, and `rcar_pcie_set_inbound()`. All operate on `struct rcar_pcie` from `pcie-rcar.h`.

Control flow: Callers map the controller and then use these helpers during probe, resume, resource-window setup, and config-space operations. `rcar_pcie_wait_for_phyrdy()` polls `PCIEPHYSR.PHYRDY` with millisecond sleeps. `rcar_pcie_wait_for_dl()` polls `PCIETSTR.DATA_LINK_ACTIVE` with short delays. Outbound setup disables the translation window, computes a 128-byte unit mask, writes lower/upper PCIe address registers, and enables memory or I/O space. Inbound setup writes local CPU and optional PCIe root-port addresses as a paired lower/upper 64-bit window.

State and persistence: The file stores no state. It mutates hardware registers through the mapped controller base. Address windows persist in controller registers until explicitly reprogrammed or reset.

Dependencies/integration: Depends on Linux PCI resource helpers such as `resource_entry`, `pci_pio_to_address()`, `roundup_pow_of_two()`, and `upper_32_bits()/lower_32_bits()`. The helper API is the narrow shared contract consumed by `pcie-rcar-host.c` and R-Car endpoint code.

Risks: `rcar_rmw32()` shifts masks by byte offset and assumes the caller passes register-relative masks correctly. Window masks round sizes up, so caller-side range splitting must prevent unwanted overmapping. `rcar_pcie_set_inbound()` uses adjacent entries for 64-bit windows, so index management is critical.

Test signals: Compile/link coverage for both R-Car host and endpoint users, successful PHY/data-link polling on hardware, config/resource enumeration through programmed outbound windows, DMA through inbound mappings, and suspend/resume reprogramming of windows.
