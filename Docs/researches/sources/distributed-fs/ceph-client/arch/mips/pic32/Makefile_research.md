## sources/distributed-fs/ceph-client/arch/mips/pic32/Makefile

### Purpose
This Makefile selects PIC32 common and PIC32MZDA-specific object directories based on kernel configuration.

### Important APIs, Types, And Functions
It adds `common/` for `CONFIG_MACH_PIC32` and `pic32mzda/` for `CONFIG_PIC32MZDA`.

### Control Flow
Build inclusion is purely conditional. Common reset/IRQ support is built for all PIC32 machines, while PIC32MZDA code is included only for that machine type.

### State, Persistence, And Dependencies
No runtime state exists. Build state depends on Kconfig symbols from `pic32/Kconfig`.

### Integration Points
This is the build bridge from top-level MIPS platform selection to PIC32 subdirectories.

### Risks
Future PIC32 variants would need additional directory rules or they may accidentally reuse MZDA-only code.

### Test Signals
`make` should include only common objects for generic PIC32 and include `pic32mzda/` objects when `CONFIG_PIC32MZDA=y`.
