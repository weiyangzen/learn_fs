# sources/distributed-fs/ceph-client/include/linux/rtsx_pci.h

## Purpose
`rtsx_pci.h` is the main register map and core interface for Realtek PCIe card-reader controllers.

## Important APIs, types, and functions
The file defines host controller registers (`RTSX_HCBAR`, `RTSX_HDBAR`, interrupt masks), SD/MS/card-power/clock/OCP/PHY/PCIe/L1 substate register constants, transfer state/result constants, DMA/SG buffer sizing, device IDs, package/version helpers, phase macros, and direct MMIO helpers `rtsx_pci_readl()`/`writel()` variants. Key types are `struct pcr_handle`, `struct pcr_ops`, `enum PDEV_STAT`, `enum ASPM_MODE`, `struct rtsx_cr_option`, `struct rtsx_hw_param`, and `struct rtsx_pcr`. APIs include `rtsx_pci_start_run()`, register/PHY read-write helpers, command queue helpers, DMA map/unmap/transfer, ping-pong buffer read/write, pull control, clock/power/voltage/card-exist helpers, `rtsx_pci_complete_unfinished_transfer()`, `rtsx_pci_get_cmd_data()`, `rtsx_pci_write_be32()`, and `rtsx_pci_update_phy()`.

## Control flow, state, and persistence
The PCI core maps BARs, allocates reserved command/SG buffers, fills `struct rtsx_pcr`, and uses batched register commands (`ci`) to program hardware. DMA helpers build SG descriptors in the reserved buffer, trigger transfers, and complete through interrupt/completion state. Chip-specific `pcr_ops` customize PHY access, LED, power, output voltage, ASPM/L1 substate, OCP, and vendor settings. Persistent runtime state includes current clock, card presence flags, interrupt enables, DMA error count, OCP/OVP status, ASPM state, chip revision, pull-control tables, and platform slots.

## Dependencies and integration points
It depends on PCI, scheduler/completion/mutex/spinlock primitives, scatterlist/DMA APIs through implementation files, and `rtsx_common.h`. It integrates the Realtek PCI core with SD/MMC and MemoryStick platform child drivers, runtime PM, MSI/INTx interrupts, card-detect delayed work, over-current protection, voltage switching, and PHY tuning for many Realtek device IDs.

## Risks and test signals
Risks include register constant drift across chip variants, DMA descriptor length limits, command-buffer overflow (`MAX_RW_REG_CNT`/reserved buffer), missed interrupts/completions, ASPM/L1 power-state races, unsafe voltage/OCP thresholds, and PHY tuning regressions. Test signals include probe on supported PIDs/revisions, register read/write batching, SG DMA read/write, card insertion/removal, suspend/resume/runtime PM, voltage switch, OCP interrupt handling, ASPM toggling, and SD high-speed tuning.
