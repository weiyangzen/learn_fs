<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h

### Purpose
`pontis.h` declares Pontis MS300 board support for the ICE1724/VT1720 core.

### Important APIs, Types, And Functions
It defines `PONTIS_DEVICE_DESC`, dummy subdevice ID `VT1720_SUBDEVICE_PONTIS_MS300`, and declares `snd_vt1720_pontis_cards[]`.

### Control Flow
The core includes this header and scans the Pontis card table. A match or model override invokes `pontis_init` and `pontis_add_controls`.

### State And Persistence
The header is static metadata only; runtime state and synthetic EEPROM live in `pontis.c`.

### Dependencies And Integration Points
It integrates with `ice1724.c` `card_tables[]` and with device-description aggregation elsewhere in the driver family.

### Risks
Because the ID is explicitly dummy, automatic hardware matching may be less robust than boards with real subvendor IDs.

### Test Signals
Build linkage, model override `ms300`, and successful control/proc creation from `pontis.c` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h -->
