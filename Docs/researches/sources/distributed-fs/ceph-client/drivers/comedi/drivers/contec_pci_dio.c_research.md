# sources/distributed-fs/ceph-client/drivers/comedi/drivers/contec_pci_dio.c

Purpose: Provides a compact PCI auto-configured Comedi driver for the Contec PIO1616L digital I/O board, exposing 16 digital inputs and 16 digital outputs.

Important APIs/types/functions: The register map is `PIO1616L_DI_REG` at offset 0 and `PIO1616L_DO_REG` at offset 2. Functional entry points are `contec_auto_attach()`, `contec_di_insn_bits()`, and `contec_do_insn_bits()`, plus the PCI probe/remove wrapper.

Control flow: PCI probe calls `comedi_pci_auto_config()`. Attach enables the PCI device, uses BAR0 as `dev->iobase`, allocates two subdevices, configures subdevice 0 as 16-channel DI with word reads, and subdevice 1 as 16-channel DO with word writes. DO instruction bits use `comedi_dio_update_state()` to update only masked bits, write `s->state` to the DO register, and return the cached state.

State and persistence: State is only `dev->iobase` and the Comedi DO `s->state`. Hardware output latches persist until changed or reset; no readback register is used for DO. There is no command-mode or interrupt state.

Dependencies and integration points: Depends on Comedi PCI helpers and PCI vendor ID `PCI_VENDOR_ID_CONTEC` with device `0x8172`. Detach uses `comedi_pci_detach()`.

Risks: Minimal driver, but it assumes BAR0 I/O layout and returns cached DO state rather than hardware readback. There is no IRQ, debounce, or edge event support. Test signals include probe, DI word reads, masked DO updates preserving previous bits, remove cleanup, and behavior after reset where cached state may differ from hardware until first write.
