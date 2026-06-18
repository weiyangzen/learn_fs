<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/dino.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/dino.c

## Purpose
`dino.c` manages Dino/Cujo GSC-to-PCI bridges on PA-RISC systems. It provides PCI config-space access, I/O port emulation, local interrupt masking/demultiplexing, card-mode and bridge-mode initialization, PCI bus/resource fixups, and root bus creation.

## Important APIs, Types, And Functions
`struct dino_device` embeds `struct pci_hba_data`, a spinlock, interrupt mask state, GSC IRQ transaction data, and local-to-global IRQ mapping. Important functions include `dino_cfg_read()`, `dino_cfg_write()`, generated `dino_in/out*()` I/O port accessors, IRQ chip callbacks `dino_mask_irq()`, `dino_unmask_irq()`, optional `dino_set_affinity_irq()`, ISR `dino_isr()`, IRQ assignment/fixup helpers, `dino_card_setup()`, `dino_card_fixup()`, `dino_fixup_bus()`, `dino_card_init()`, `dino_bridge_init()`, `dino_common_init()`, and `dino_probe()`.

## Control Flow
The PA-RISC driver registers at `arch_initcall`. Probe identifies Dino, Cujo, and card-mode variants, reserves MMIO, applies Cujo 2.0 CCIO workaround when configured, allocates and maps `dino_device`, initializes card-mode hardware or bridge-mode resource windows, performs common interrupt and I/O-port setup, then creates a PCI root bus with Dino config ops. The bus is scanned, resources assigned, devices added, and the global `dino_current_bus` advances.

Config access serializes on `dinosaur_pen`, writes `DINO_PCI_ADDR`, then reads or writes `DINO_CONFIG_DATA`; writes perform an extra vendor/product read to avoid Dino address stepping. I/O port ops use the same address register with `DINO_IO_DATA`.

Interrupt flow maps each local Dino input to a Linux IRQ via `gsc_assign_irq()`. The top ISR reads and clears `DINO_IRR0`, handles each pending local bit through `generic_handle_irq()`, then checks `DINO_ILR` for still-asserted level interrupts and loops up to 100 times before rate-limited warnings.

## State And Persistence
Per-bridge state persists in `dino_device` and `dev->dev.platform_data`. Hardware state includes PCI address/config registers, IMR, IAR0, bridge feature/control registers, MMIO decode windows, port resources, and card-mode PCI command/timing registers. PCI bus numbering persists through the global `dino_current_bus`.

## Dependencies And Integration Points
The driver integrates with PA-RISC GSC IRQ helpers, PCI core root-bus/resource APIs, CCIO IOMMU/resource helpers, architecture HBA data, optional Tulip and Cirrus PCI fixups, and PARISC firmware inventory.

## Risks
The code assumes PCI scanning is single-threaded because of the global bus counter. SMP interrupt comments warn that broadcast EIR behavior is poor. Card-mode Dino has limited MMIO support and explicitly rejects PCI-PCI bridges. IRQ fixup for unassigned devices is enabled but platform mappings vary. Config and I/O access depend on the spinlock and Dino address-stepping workaround. Some error paths after allocations/requested resources do not fully unwind.

## Test Signals
Boot tests should cover built-in Dino, Cujo, and card-mode Dino, config read/write correctness, I/O port access, level-triggered shared IRQs, stuck interrupt warnings, SMP affinity updates, PCI bridge resource assignment, card-mode 8 MB LMMIO allocation, Cirrus CardBus and Tulip fixups, Cujo 2.0 workaround interaction with CCIO, and root bus numbering across multiple bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/dino.c -->
