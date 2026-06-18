# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-microchip-host.c

## Purpose
Implements the Microchip PolarFire SoC AXI PCIe host controller using PLDA XpressRich-style register blocks. It provides Microchip-specific register mapping, interrupt/event decoding, ECC/error masking, MSI setup fixups, clock enablement, inbound/outbound address translation, and ECAM host probing.

## Important APIs, Types, And Functions
Key state is `struct mc_pcie`, which embeds `struct plda_pcie_rp` and stores bridge/control register bases. Event tables map PCIe, SEC, DED, and PLDA local interrupt bits into Linux hwirqs. Important functions include `mc_host_probe()`, `mc_platform_init()`, `mc_disable_interrupts()`, `mc_get_events()`, `mc_ack_event_irq()`, `mc_mask_event_irq()`, `mc_unmask_event_irq()`, `mc_pcie_setup_inbound_ranges()`, and `mc_pcie_enable_msi()`.

## Control Flow
Platform probe allocates the global `port`, maps either split `bridge`/`ctrl` resources or the legacy `apb` resource, disables and clears interrupts, reads MSI vector count/address from hardware, enables optional Fabric Interface clocks, and delegates to `pci_host_common_probe()`. ECAM setup calls `mc_platform_init()`, which programs config-space ATR window 0, fixes MSI capability fields in root-port config space, configures outbound memory windows, sets inbound ranges from `dma-ranges` or noncoherent MPFS defaults, installs Microchip event ops/chip, and initializes PLDA interrupts.

## State And Persistence
Persistent state is mostly hardware register state: ATR tables, MSI capability fields, interrupt masks/status, ECC bypass bits, and inbound windows. Driver state is devm-managed except the file-scope `port`, which reflects only one active controller context.

## Dependencies And Integration Points
Integrates with `pci-host-common`, `pci-ecam`, PLDA common code in `pcie-plda-host.c`, device tree resources and `dma-ranges`, optional clocks `fic0` through `fic3`, Linux irq domains, and PCI host enumeration.

## Risks
The file-scope `port` is fragile if multiple controllers are ever supported. Interrupt mask polarity differs among event classes and depends on `event_descs` correctness. Inbound ATR setup has hardware-specific noncoherent assumptions. MSI capability rewriting must match the bitstream-provided vector count and MSI address.

## Test Signals
Probe should log ECAM setup and enumerate downstream devices on `microchip,pcie-host-1.0`. Useful signals include MSI delivery, INTx delivery, SEC/DED/AER error interrupts, DMA coherent and noncoherent DMA traffic, fallback legacy `apb` resource binding, and boot with varied `dma-ranges`.
