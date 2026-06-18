<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h

### Purpose
`maya44.h` declares the ESI Maya44 board identity and card table for the ICE1724 core.

### Important APIs, Types, And Functions
It defines `MAYA44_DEVICE_DESC`, `VT1724_SUBDEVICE_MAYA44`, and declares `snd_vt1724_maya44_cards[]`.

### Control Flow
The core includes the header and scans `snd_vt1724_maya44_cards` during EEPROM/model matching. A match routes board initialization to `maya44_init` and control registration to `maya44_add_controls`.

### State And Persistence
The header has no mutable state. Its constants determine detection and user-facing device description aggregation.

### Dependencies And Integration Points
It integrates with `ice1724.c` card table discovery and relies on `maya44.c` for the table definition and synthetic EEPROM payload.

### Risks
Wrong constants would prevent the board-specific codec setup from running, leaving the core with generic behavior that cannot drive the Maya44 codecs properly.

### Test Signals
Build linkage of `snd_vt1724_maya44_cards`, model override `maya44`, and detection of subvendor `0x34315441` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h -->
