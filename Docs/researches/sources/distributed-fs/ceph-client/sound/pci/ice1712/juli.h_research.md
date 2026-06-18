<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h

### Purpose
`juli.h` is the public board header that lets the ICE1724 core advertise and match ESI Juli@ cards.

### Important APIs, Types, And Functions
It defines `JULI_DEVICE_DESC`, `VT1724_SUBDEVICE_JULI`, and declares `extern struct snd_ice1712_card_info snd_vt1724_juli_cards[]`.

### Control Flow
The core includes this header, adds `snd_vt1724_juli_cards` to `card_tables[]`, and uses the subdevice ID or model name to call the `juli.c` initialization and control-building callbacks.

### State And Persistence
There is no runtime state in the header. The subdevice ID is a stable matching constant, while `snd_vt1724_juli_cards[]` points to synthetic EEPROM and callbacks in `juli.c`.

### Dependencies And Integration Points
The declaration depends on `struct snd_ice1712_card_info` being visible through the including C file. It integrates with module device descriptions and the board table scan in `ice1724.c`.

### Risks
Incorrect subdevice or description strings would make the board unreachable by automatic detection or model override. The header has no guards beyond the include guard and relies on `juli.c` to define the table exactly once.

### Test Signals
Build success, `modinfo`/device description inclusion, and successful probe of a card with subvendor `0x31305345` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h -->
