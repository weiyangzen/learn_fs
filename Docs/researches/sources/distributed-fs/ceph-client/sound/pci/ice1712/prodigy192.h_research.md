<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h

### Purpose
`prodigy192.h` declares AudioTrak Prodigy 192 board matching constants and GPIO pins used by the optional MI/ODI/O AK4114 interface.

### Important APIs, Types, And Functions
It defines `PRODIGY192_DEVICE_DESC`, STAC9460 I2C address `PRODIGY192_STAC9460_ADDR`, subdevice `VT1724_SUBDEVICE_PRODIGY192VE`, AK4114 GPIO masks `VT1724_PRODIGY192_CS/CCLK/CDOUT/CDIN`, and declares `snd_vt1724_prodigy192_cards[]`.

### Control Flow
The core uses the table declaration during board matching. `prodigy192.c` uses the address and GPIO masks to access STAC9460 and bit-bang AK4114 reads/writes.

### State And Persistence
No mutable state is defined. The constants encode hardware wiring and matching identity.

### Dependencies And Integration Points
It integrates with `ice1724.c` card tables and the low-level GPIO protocol in `prodigy192.c`.

### Risks
Incorrect GPIO masks would break optional S/PDIF daughtercard detection and access. Incorrect codec address would make all STAC controls nonfunctional.

### Test Signals
Successful Prodigy 192 probe, STAC I2C access at address `0x54`, and AK4114 access over GPIO8-11 validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h -->
