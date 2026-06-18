# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1720.c Research

Provides PCI auto-config support for the Advantech PCI-1720U isolated 4-channel analog output board. It also exposes the 4-bit BoardID switch as a digital input subdevice.

`pci1720_ao_insn_write()` programs per-channel range bits, writes 12-bit DAC data as LSB/MSB bytes, waits for conversion settling, and updates Comedi readback. `pci1720_di_insn_bits()` reads the board ID register. `pci1720_auto_attach()` enables PCI BAR2, allocates AO and BoardID DI subdevices, allocates AO readback, and disables synchronized output mode.

The driver intentionally does not reset analog outputs on attach so jumper-selected hot-reset behavior can preserve hardware output state. Each AO instruction write reads the current range register, updates only the target channel bits, writes the sample, and records the last value in `s->readback`. There is no command streaming or IRQ state. Runtime persistence is limited to hardware DAC/range registers and Comedi AO readback.

Dependencies are Comedi PCI helpers, raw I/O port access, `comedi_alloc_subdev_readback()`, and `module_comedi_pci_driver()`. The file status is untested. Risks include unsynchronized-output mode being the only supported mode, range register read/modify/write affecting adjacent channels, and current-sink range semantics depending on jumpers. Tests should verify BoardID reads, per-channel range isolation, DAC byte order, readback updates, no attach-time output reset, and sync control set to immediate update.
