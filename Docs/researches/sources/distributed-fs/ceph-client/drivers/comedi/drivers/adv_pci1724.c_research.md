# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adv_pci1724.c Research

Provides the Comedi PCI driver for the Advantech PCI-1724U. It exposes 32 analog output channels plus internal calibration subdevices for offset and gain.

`adv_pci1724_insn_write()` is shared by normal AO, offset calibration, and gain calibration; it takes the target DAC mode from `s->private`, waits for DAC idle with `adv_pci1724_dac_idle()`, writes a combined control/data word, and updates readback. `adv_pci1724_auto_attach()` enables PCI, reads/logs the board ID, allocates three subdevices, assigns mode-specific private data, and allocates readback.

Attach creates subdevice 0 for user AO, subdevice 1 for offset calibration, and subdevice 2 for gain calibration. All three use the same write path and the same 14-bit data width. Writes disable synchronous mode before programming a channel, poll `DACSTAT` until idle, and then issue a mode/channel/group/data control word. State persists in DAC/calibration hardware and per-subdevice readback arrays only.

Dependencies are Comedi PCI, raw 32-bit port I/O, `comedi_timeout()`, Comedi internal calibration subdevice flags, and `module_comedi_pci_driver()`. Risks include calibration values strongly changing real output range, busy-wait timeout behavior, and the nominal 0-20 mA versus 4-20 mA range distinction being calibration-dependent rather than hardware-distinct. Tests should cover board ID read, DAC idle timeout, mode selection per subdevice, readback allocation for all three subdevices, maxdata/range mapping, and sync mode forced off before writes.
