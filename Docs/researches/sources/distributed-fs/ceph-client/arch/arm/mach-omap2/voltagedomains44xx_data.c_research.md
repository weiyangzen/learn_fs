<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c

### Purpose
`voltagedomains44xx_data.c` defines OMAP4 scalable MPU, IVA, and CORE voltage domains plus wakeup domain metadata.

### Important APIs, Types, And Functions
It exports `omap44xx_voltagedomains_init()` and defines VFSM instances, `omap4_voltdm_mpu`, `omap4_voltdm_iva`, `omap4_voltdm_core`, `omap4_voltdm_wkup`, and the OMAP4 domain list.

### Control Flow
Init selects OMAP443x or OMAP446x OPP voltage tables if available, attaches OMAP4 VP and VC parameter structures to each scalable domain, sets sysclk name to `sys_clkin_ck`, and registers the list.

### State, Persistence, And Dependencies
Static domain objects persist and include OMAP4 PRM register callbacks, VC/VP pointers, VFSM setup registers, OPP tables, and clock-name state. Dependencies include OMAP4 PRM headers and OPP data.

### Integration Points
Generic voltage late init uses these objects to initialize VC/VP for OMAP4 DVFS and low-power transitions.

### Risks
Unsupported OMAP4 variants may not receive voltage tables. Incorrect sysclk naming prevents late init from calculating VC/VP timing. OMAP4 and OMAP5 share some VC/VP data, so changes have cross-SoC impact.

### Test Signals
OMAP443x and OMAP446x boots should register all domains and initialize VC/VP with a valid `sys_clkin_ck` rate; DVFS should scale MPU, IVA, and CORE independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains44xx_data.c -->
