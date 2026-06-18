# sources/distributed-fs/ceph-client/arch/arm/plat-orion/pcie.c

Purpose: Implements Orion PCIe controller setup, link/reset helpers, DRAM decode window programming, interrupt enablement, and PCI configuration-space access methods.

Important APIs/functions: `orion_pcie_dev_id`, `orion_pcie_rev`, `orion_pcie_link_up`, `orion_pcie_x4_mode`, `orion_pcie_get_local_bus_nr`, `orion_pcie_set_local_bus_nr`, `orion_pcie_reset`, `orion_pcie_setup`, `orion_pcie_rd_conf`, `orion_pcie_rd_conf_tlp`, `orion_pcie_rd_conf_wa`, and `orion_pcie_wr_conf`. Internal `orion_pcie_setup_wins()` programs PCIe BARs and address decode windows from `mv_mbus_dram_info()`.

Control flow: Setup first disables BARs/windows, creates up to four DRAM windows, rounds total DRAM size to a power of two for BAR1, enables IO/memory/master in the PCI command register, and enables INTx lines A-D. Reset asserts a debug soft-reset bit, polls link state up to roughly 200 ms, and clears reset. Config reads write an encoded bus/device/function/register address to `PCIE_CONF_ADDR_OFF`, read data, and shift byte/word subfields; workaround readers either use header-log data for nonlocal/function reads or direct memory-window reads.

State and persistence: All state is hardware register state in the PCIe controller. Local bus number is stored in the status register fields. No software locks are used, so callers must serialize config access at the PCI host layer.

Dependencies/integration: Depends on Linux PCI APIs, MBus DRAM target information, ARM PCI host glue, `plat/pcie.h`, and `plat/addr-map.h`. Used by Orion machine PCI setup during host bridge initialization and enumeration.

Risks/tests: DRAM size rounding can expose a BAR aperture larger than installed memory if windows are not otherwise constrained. Config write supports only 1/2/4-byte sizes; invalid sizes return `PCIBIOS_BAD_REGISTER_NUMBER`, but read paths do not reject odd sizes. Link-down, multifunction, and local-bus behavior require hardware-specific tests. Validate config-space enumeration, BAR/window registers, reset timing, and INTx delivery.
