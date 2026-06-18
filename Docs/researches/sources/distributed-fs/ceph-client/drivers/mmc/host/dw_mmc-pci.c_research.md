# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pci.c

Purpose: adapts the generic DesignWare MMC core to a Synopsys PCI device, supplying PCI enablement, BAR mapping, default capabilities, bus frequency, FIFO depth, shared IRQ settings, and remove handling.

Important APIs and functions: `dw_mci_pci_probe` is the PCI probe path, `dw_mci_pci_remove` tears down via `dw_mci_remove`, and `pci_drv_data` supplies common MMC caps. The PCI ID table matches vendor `0x700` and device `0x1107`.

Control flow: probe enables the PCI device with pcim, allocates a `dw_mci` through `dw_mci_alloc_host`, fills IRQ, shared IRQ flag, FIFO depth 32, detect delay 200 ms, 33 MHz bus rate, and capabilities, maps BAR 2 through `pcim_iomap_region`, enables bus mastering, calls `dw_mci_probe`, and stores driver data. Remove fetches the host and calls the shared DW removal path.

State and persistence: no private PCI-specific state exists beyond the `dw_mci` object. PCI managed resources handle device enable and BAR lifetime; shared DW state holds request/DMA/PIO/runtime data.

Dependencies and integration points: depends on Linux PCI, PCI endpoint function BAR constants, shared DW core, shared PM ops, and MMC capability bits. It reuses all request/interrupt/PM behavior from `dw_mmc.c`.

Risks: BAR 2 and 33 MHz bus assumptions are hard-coded for the matched Synopsys device. No device-specific tuning or voltage hooks are provided. IRQ is shared, so interrupt status handling must be robust. The vendor ID value is not a normal public PCI vendor ID, suggesting endpoint/test-device usage.

Test signals: PCI enumeration with the matching ID, BAR 2 mapping, shared IRQ operation, `dw_mci_probe` success, card-detect delay behavior, and read/write tests in PIO/DMA modes.
