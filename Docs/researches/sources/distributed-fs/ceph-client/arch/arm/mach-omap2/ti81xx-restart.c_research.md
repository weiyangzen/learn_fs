<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c

### Purpose
`ti81xx-restart.c` implements the TI81xx SoC restart hook by requesting a cold global reset through PRM registers.

### Important APIs, Types, And Functions
The sole API is `ti81xx_restart(enum reboot_mode mode, const char *cmd)`. It writes `TI81XX_GLOBAL_RST_COLD` into `TI81XX_PRM_DEVICE_RSTCTRL` using `omap2_prm_set_mod_reg_bits()`.

### Control Flow
The function sets the cold-reset request bit and then spins forever, relying on the hardware reset to interrupt execution.

### State, Persistence, And Dependencies
Persistent state is the PRM reset-control bit. It depends on TI81xx PRM addressing and the common ARM restart path wiring this function as the machine restart callback.

### Integration Points
Machine setup code uses this as the restart method for TI81xx-class OMAP platforms.

### Risks
There is no timeout or fallback path if the reset request fails. The comment notes warm reset is not used because it may require clock bypass preparation.

### Test Signals
The observable test is a clean reboot from kernel restart paths on TI81xx hardware, with no return from the restart callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/ti81xx-restart.c -->
