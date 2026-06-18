# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h

### Purpose
`sgi/gio.h` documents and defines SGI GIO bus address ranges and board-ID bit extraction for Indigo/Indy/Indigo2-era expansion devices.

### Important APIs, Types, And Functions
Macros include `GIO_ID`, `GIO_32BIT_ID`, `GIO_REV`, `GIO_64BIT_IFACE`, `GIO_ROM_PRESENT`, `GIO_VENDOR_CODE`, and slot base addresses `GIO_SLOT_GFX_BASE`, `GIO_SLOT_EXP0_BASE`, and `GIO_SLOT_EXP1_BASE`.

### Control Flow
There is no executable flow. GIO probing code reads a slot ID value and uses the macros to decode product ID, revision, interface width, ROM presence, and vendor bits.

### State, Persistence, Dependencies, And Integration
State is hardware slot address space and ID values returned by devices. Integration is with SGI platform bus probing and drivers for GIO graphics, network, and expansion devices.

### Risks
Some IDs are 8-bit with undefined high bits; callers must mask before comparing. Slot availability differs by machine model, so blindly probing fixed ranges can fault or misdetect devices.

### Test Signals
Boot SGI IP22-class configs with known GIO devices, verify ID decode and slot resource assignment, and test absent-slot probing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/gio.h -->
