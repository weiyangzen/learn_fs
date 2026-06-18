<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h

### Purpose
`phase.h` defines the Terratec/Terrasoniq PHASE board identities, declares their card table, and centralizes PHASE28 GPIO bit assignments.

### Important APIs, Types, And Functions
It defines `PHASE_DEVICE_DESC`, `VT1724_SUBDEVICE_PHASE22`, `VT1724_SUBDEVICE_PHASE28`, `VT1724_SUBDEVICE_TS22`, declares `snd_vt1724_phase_cards[]`, and defines PHASE28 SPI, reset, AC97, digital-select, headphone-select, and data-mask GPIO bits.

### Control Flow
`ice1724.c` includes the header and scans `snd_vt1724_phase_cards`; `phase.c` includes the header and uses the GPIO constants when resetting and programming the PHASE28 WM codec.

### State And Persistence
There is no mutable state. GPIO bit definitions are hardware contract constants used to avoid duplicated magic numbers in the implementation.

### Dependencies And Integration Points
It integrates with the core board table and with `phase28_spi_write`/`phase28_init` in `phase.c`.

### Risks
Wrong GPIO constants would corrupt codec programming or reset behavior. The header exposes constants only for PHASE28; PHASE22 GPIO wiring lives in `phase.c` AKM private data.

### Test Signals
Compile-time use of the constants, correct detection of the three subdevices, and successful PHASE28 codec initialization are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h -->
