<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/parisc/Makefile

## Purpose
This Makefile maps PA-RISC Kconfig symbols to driver objects and documents ordering constraints required for bus enumeration, IRQ regions, PCI, EISA, and IOMMU setup.

## Important APIs, Types, And Functions
Object mappings include `iosapic.o`, `sba_iommu.o`, `lba_pci.o`, `ccio-dma.o`, `gsc.o`, `lasi.o asp.o`, `wax.o`, EISA objects, `hppb.o`, `dino.o`, `superio.o`, `led.o`, `pdc_stable.o`, and always-built `power.o`.

## Control Flow
The build order is the only flow. Comments specify that CCIO must come before potential subdevices, GSC before LASI/WAX, ASP/WAX before EISA adapters for IRQ regions, and EISA before PCI so it gets an IRQ region.

## State And Persistence
No runtime state is present. The ordering persists in the linked kernel object order and can affect initcall probing behavior on PA-RISC hardware.

## Dependencies And Integration Points
The Makefile consumes symbols defined in `Kconfig` and produces object inclusion for the architecture's platform bus, PCI, IOMMU, LED, stable-storage, and power drivers.

## Risks
Reordering can break early resource/IRQ ownership and bus discovery. Conditional inclusion must match Kconfig dependencies; otherwise objects may reference unavailable symbols or probe before required infrastructure is initialized.

## Test Signals
Use build tests for relevant Kconfig combinations and boot tests on systems with CCIO, GSC/LASI/ASP/WAX, EISA, Dino PCI, LBA PCI, SuperIO, chassis LEDs, and stable storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Makefile -->
