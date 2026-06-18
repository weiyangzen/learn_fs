## sources/distributed-fs/ceph-client/arch/mips/power/Makefile

### Purpose
This Makefile includes MIPS hibernation support objects when hibernation is enabled.

### Important APIs, Types, And Functions
For `CONFIG_HIBERNATION`, it builds `cpu.o`, `hibernate.o`, and `hibernate_asm.o`.

### Control Flow
Build inclusion is conditional on the hibernation Kconfig symbol.

### State, Persistence, And Dependencies
No runtime state exists. The object list provides architecture callbacks used by the generic suspend/hibernate core.

### Integration Points
The generated objects implement processor state save/restore, resume, and low-level image copy/return.

### Risks
Partial object selection is not supported; all three files are required for a functional hibernation path.

### Test Signals
Build with `CONFIG_HIBERNATION=y` and verify symbols `swsusp_arch_suspend`, `swsusp_arch_resume`, and processor state hooks are linked.
