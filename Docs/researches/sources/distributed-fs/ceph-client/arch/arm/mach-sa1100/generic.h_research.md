<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h

### Purpose
Declares shared SA1100 board support APIs and helpers.

### Important APIs, Types, And Functions
Declares common init functions, restart/late-init hooks, memory bank macro `SET_BANK`, memory bus control, cpufreq helpers, MTD/MCP/LCD/PCMCIA/fixed-regulator registration helpers, `sa11xx_clk_init()`, and PM init stubs.

### Control Flow
No direct flow; board files call these functions from machine map/init/fixup callbacks.

### State, Persistence, And Dependencies
State lives in `generic.c` or board files. Depends on cpufreq, reboot, platform data forward declarations, and config-dependent PM.

### Integration Points
Included by Assabet, Collie, H3600, H3xxx, and common code.

### Risks
The broad helper surface makes board initialization order important. `SET_BANK` assumes a `meminfo` pointer named `mi`.

### Test Signals
Compile coverage across board configs and boot of each board validate declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/generic.h -->
