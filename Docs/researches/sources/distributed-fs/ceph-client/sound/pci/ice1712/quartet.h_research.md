<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h

### Purpose
`quartet.h` declares the Infrasonic Quartet board identity and card table.

### Important APIs, Types, And Functions
It defines `QTET_DEVICE_DESC`, subdevice ID `VT1724_SUBDEVICE_QTET`, and declares `snd_vt1724_qtet_cards[]`.

### Control Flow
The core includes the header, scans the Quartet card table, and invokes `qtet_init` and `qtet_add_controls` when the subvendor or model matches.

### State And Persistence
The header is static metadata only. Runtime clock/register/cache state lives in `quartet.c`.

### Dependencies And Integration Points
It integrates with `ice1724.c` board aggregation and the table definition in `quartet.c`.

### Risks
Incorrect subdevice matching would prevent the custom CPLD/clock setup from running, which is essential for this board.

### Test Signals
Build linkage, model override `quartet`, detection of subdevice `0x30305349`, and presence of Quartet-specific clock/control surfaces validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h -->
