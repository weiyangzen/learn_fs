# sources/distributed-fs/ceph-client/drivers/comedi/drivers/cb_pcidda.c

Purpose: Provides PCI auto-configured Comedi support for Measurement Computing PCI-DDA02/04/08 boards in 12-bit and 16-bit variants. The implemented feature set is simple analog output plus two 8255 DIO subdevices; command-mode streaming is not supported.

Important APIs/types/functions: Board selection uses `enum cb_pcidda_boardid`, `struct cb_pcidda_board`, and `cb_pcidda_boards[]`. Per-device state lives in `struct cb_pcidda_private`, holding the DAC I/O base, cached calibration register bits, current AO range per channel, and a software copy of 128 EEPROM words. Key functions are `cb_pcidda_auto_attach()`, `cb_pcidda_ao_insn_write()`, `cb_pcidda_read_eeprom()`, `cb_pcidda_serial_out()`, `cb_pcidda_serial_in()`, `cb_pcidda_write_caldac()`, and `cb_pcidda_calibrate()`.

Control flow: PCI probe passes the table `driver_data` board index to `comedi_pci_auto_config()`. Attach enables the PCI device, stores BAR2 as `dev->iobase` for 8255 access and BAR3 as the DAC/calibration I/O base, allocates three subdevices, configures the AO subdevice from board metadata, initializes two 8255 subdevices at offsets 0 and `I8255_SIZE`, reads all EEPROM calibration words through bit-banged serial I/O, and calibrates each AO channel. AO writes recalibrate only if the requested range differs from cached `ao_range[channel]`, program the DAC control register with channel/range/unipolar bits, then write each sample to the channel data register.

State and persistence: The driver caches EEPROM contents, last selected range per AO channel, and the last output value only through hardware state; there is no Comedi readback allocation for AO. Calibration DAC settings are written from EEPROM on attach and whenever range changes. Persistent hardware data is the EEPROM calibration table; host-side state exists only for the attached device lifetime.

Dependencies and integration points: Depends on Comedi PCI helpers and `comedi_8255` for DIO. It integrates with CB PCI IDs `0x0020` through `0x0025`, the Comedi range model, and MCC/CB calibration EEPROM/caldac serial protocol. Detach is delegated to `comedi_pci_detach()`.

Risks: Serial EEPROM/caldac programming is timing-sensitive and uses port I/O delays but no locking. `ao_range[]` starts zeroed, so attach calibration writes range 0 for all channels. Range-to-EEPROM index math assumes the board's calibration layout exactly matches six ranges per channel. AO readback is not supported, so users cannot query last output through Comedi readback. Test failures are likely to show as incorrect output scaling or calibration drift rather than probe failures.

Test signals: Validate all six PCI IDs choose the correct channel count/resolution, AO writes update every channel over all six ranges, range changes trigger calibration writes, both 8255 subdevices configure/read/write banks, and EEPROM reads produce stable calibration words.
