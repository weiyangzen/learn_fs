<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h

### Purpose
`prodigy_hifi.h` declares board descriptions and subdevice IDs for the Prodigy HiFi family and Fortissimo IV.

### Important APIs, Types, And Functions
It defines `PRODIGY_HIFI_DEVICE_DESC`, `VT1724_SUBDEVICE_PRODIGY_HIFI`, `VT1724_SUBDEVICE_PRODIGY_HD2`, `VT1724_SUBDEVICE_FORTISSIMO4`, and declares `snd_vt1724_prodigy_hifi_cards[]`.

### Control Flow
The core scans `snd_vt1724_prodigy_hifi_cards` during probe. Matching entries call either `prodigy_hifi_init`/`prodigy_hifi_add_controls` or `prodigy_hd2_init`/`prodigy_hd2_add_controls`.

### State And Persistence
The header carries no mutable state. The IDs select different synthetic EEPROM arrays and codec paths in `prodigy_hifi.c`.

### Dependencies And Integration Points
It integrates with the core card table and device description string aggregation.

### Risks
The macro spans multiple product names; changing string formatting can affect module aliases/descriptions. Misassigned subdevice IDs would route boards to the wrong codec topology.

### Test Signals
Probe of all three subdevice IDs, correct ALSA `driver` names, and board-specific control sets validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h -->
