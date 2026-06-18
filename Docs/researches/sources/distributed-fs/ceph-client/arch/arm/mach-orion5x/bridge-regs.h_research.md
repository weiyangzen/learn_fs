<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h

### Purpose
`bridge-regs.h` defines Orion5x CPU bridge register virtual and physical addresses used for reset, interrupts, power management, and timers.

### Important APIs, Types, And Functions
Key macros include `CPU_CONF`, `CPU_CTRL`, `RSTOUTn_MASK`, `CPU_SOFT_RESET`, `BRIDGE_CAUSE`, `POWER_MNG_CTRL_REG`, `MAIN_IRQ_CAUSE`, `MAIN_IRQ_MASK`, and timer base constants.

### Control Flow
There is no executable flow. The macros translate from `ORION5X_BRIDGE_VIRT_BASE` or physical base to register addresses.

### State, Persistence, And Dependencies
The header has no state and depends on `orion5x.h` base-address definitions.

### Integration Points
Common init, IRQ handling, watchdog resources, restart, and board power-off/reset code use these registers.

### Risks
Register address mistakes affect early boot, interrupt delivery, watchdog registration, and restart behavior. `BRIDGE_INT_TIMER1_CLR` is a mask value rather than an address, which can be easy to misuse.

### Test Signals
Boot-time interrupt, timer, watchdog, and restart tests indirectly validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/bridge-regs.h -->
