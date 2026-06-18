# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Kconfig

Defines configuration for the cx23885 PCIe media driver and optional Altera FPGA CI module. `VIDEO_CX23885` is a tristate depending on DVB, V4L2, PCI, I2C, input, sound, and RC core support. It selects the required vb2, tuner, EEPROM, cx25840, cx2341x, ALSA PCM, and many optional frontend/tuner helpers under autoselect.

`MEDIA_ALTERA_CI` depends on `VIDEO_CX23885` and `DVB_CORE`, selects `ALTERA_STAPL`, and builds the NetUP Altera CI module when enabled.

Risks are incomplete selected dependencies or unnecessary dependency breadth. Test signals are built-in/modular/disabled builds and probe tests on boards requiring DVB, analog, ALSA, RC, and CI features.
