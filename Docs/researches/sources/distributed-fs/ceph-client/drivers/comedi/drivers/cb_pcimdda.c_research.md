# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcimdda.c

Purpose: Provides Comedi support for the Measurement Computing PCIM-DDA06-16 analog output board. It exposes six 16-bit AO channels and one 8255 DIO subdevice. Command-mode AO is not supported.

Important APIs/types/functions: The file defines the PCI ID `PCI_ID_PCIM_DDA06_16`, channel register macro `PCIMDDA_DA_CHAN()`, and 8255 base `PCIMDDA_8255_BASE_REG`. Functional entry points are `cb_pcimdda_auto_attach()`, `cb_pcimdda_ao_insn_write()`, and `cb_pcimdda_ao_insn_read()`.

Control flow: PCI probe auto-configures the Comedi driver. Attach enables PCI, uses BAR3 as `dev->iobase`, allocates two subdevices, initializes the AO subdevice with readable/writable flags and bipolar 5 V range, allocates AO readback, and initializes an 8255 DIO subdevice at offset `0x0c`. AO writes emit LSB then MSB to the channel's two byte registers; if the board jumper is in immediate update mode, MSB latches output. AO reads perform an input from the channel register to trigger simultaneous transfer when the board jumper is in simultaneous XFER mode, then return Comedi readback data.

State and persistence: Driver state is `dev->iobase` plus Comedi AO readback and DIO state. Hardware jumper state controls both output range and update mode and is invisible to software. The driver assumes factory default bipolar 5 V for the range table.

Dependencies and integration points: Depends on Comedi PCI helpers and `subdev_8255_io_init()`. It integrates with PCI vendor CB device ID `0x0053`, legacy I/O-mapped DAC registers, and Comedi readback helpers. Detach uses `comedi_pci_detach()`.

Risks: The output range and simultaneous-transfer mode cannot be detected, so the reported Comedi range may be wrong if jumpers differ. The read path has side effects by design because reads can latch simultaneous AO updates. Only byte-wide register ordering is correct for the board; changing to word writes could break hardware. Test signals include AO channel write/readback, simultaneous transfer latch behavior, 8255 DIO configuration, and probe/remove with BAR3 resources.
