# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1723.c Research

Implements the Advantech PCI-1723 Comedi driver. It exposes an 8-channel 16-bit analog output subdevice and a 16-channel grouped digital I/O subdevice.

`pci1723_ao_insn_write()` writes DAC samples to channel registers and updates readback. `pci1723_dio_insn_config()` configures a whole 8-bit group based on the requested channel, using Comedi DIO helpers and the board DIO control register. `pci1723_dio_insn_bits()` updates output state and reads back the DIO data register. `pci1723_auto_attach()` enables PCI, allocates subdevices, resets AO synchronously to midscale +/-10 V, and initializes DIO direction/state from hardware.

Attach performs a synchronous AO reset: it enters sync mode, sets each channel range, writes midscale data, strobes sync, then returns to async mode. DIO configuration maps channels 0-7 and 8-15 to low/high byte direction bits; `s->io_bits` is the software mirror, while `s->state` mirrors output data. AO state persists in DAC registers and Comedi readback. DIO direction and state are read during attach and then updated through instruction calls.

Dependencies are Comedi PCI auto attach, Comedi DIO helpers, raw I/O port operations, and subdevice readback allocation. Risks include attach-time AO reinitialization despite TODO notes about reading initial ranges/values, grouped DIO direction surprises when configuring one channel, and unimplemented calibration/current ranges. Tests should check AO reset/readback midscale, DIO group direction encoding, DIO readback after writes, PCI BAR2 enablement, and no unsupported sync mode exposed to users.
