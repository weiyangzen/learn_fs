# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-apple.c

## Purpose
`pcie-apple.c` drives Apple SoC PCIe host bridges. The controller is ECAM-compliant after initialization, so the driver mainly handles core/port bring-up, per-port interrupts, MSI routing, REFCLK/PERST sequencing, and RID-to-SID mappings needed for IOMMU/DART integration.

## Important APIs, Types, And Functions
`struct apple_pcie` holds controller state, global MSI bitmap, port list, event completion, parent IRQ fwspec, vector count, and hardware descriptor. `struct apple_pcie_port` tracks per-port MMIO, PHY, IRQ domain, RID/SID bitmap, and port index. `apple_pcie_probe()` allocates the host bridge, maps core base, initializes MSI, and calls `pci_host_common_init()` with `apple_pcie_cfg_ecam_ops`. `apple_pcie_init()` sets up each DT child port. `apple_pcie_enable_device()` and `apple_pcie_disable_device()` allocate/free RID-to-SID hardware entries for devices behind root ports.

## Control Flow, State, And Persistence
MSI setup parses `msi-ranges`, finds the wired parent IRQ domain, allocates a bitmap, and creates a PCI MSI parent domain. Each port setup asserts PERST, enables app/ref clocks, waits for PHY refclk acks, deasserts PERST, waits for port ready, creates a 32-hwirq port IRQ domain, programs MSI doorbell/mapping registers, discovers RID/SID table size by write/read probing, registers link up/down IRQ handlers, starts LTSSM, and waits briefly for link-up completion. State is in bitmaps and port lists; hardware register state is set during probe and not persisted to storage.

## Dependencies, Integration Points, Risks, And Test Signals
The driver binds `"apple,pcie"` and `"apple,t6020-pcie"` with `hw_info` offsets. It integrates with generic ECAM/common host code, OF IRQ parsing, GPIO PERST, IRQ domains, generic MSI library, DART/IOMMU mapping via `iommu-map`, and PCI host bridge `enable_device`/`disable_device` hooks. Risks include fixed 32-bit MSI doorbell assumptions, `msi-ranges` parsing, RID/SID table exhaustion, REFCLK handshake timeouts, and per-generation offsets. Test port ready/link IRQs, INTx and MSI/MSI-X, RID-to-SID mapping/release, and absence of MSI/RID/completion/link errors.
