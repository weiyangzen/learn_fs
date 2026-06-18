# sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h

### Purpose
`reboot.h` exposes machine-specific reboot and halt hooks for MIPS platform code.

### Important APIs, Types, And Functions
The exported state is two function pointers: `_machine_restart(char *command)` and `_machine_halt(void)`.

### Control Flow
Generic reboot/halt paths call the installed platform hook. Platform setup assigns these pointers during boot.

### State, Persistence, Dependencies, And Integration
State is the currently installed reboot/halt implementation pointer; there is no persistent storage. Integration is with `kernel/reboot.c`-style generic shutdown paths and platform firmware or board reset drivers.

### Risks
Null or incorrectly installed hooks can hang shutdown. The restart command string lifetime and platform firmware expectations must match the implementation.

### Test Signals
Boot each MIPS platform config and exercise `reboot`, `halt`, and panic-restart paths; verify hook installation during platform init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/reboot.h -->
