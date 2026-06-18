<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c

### Purpose
`voltagedomains3xxx_data.c` defines OMAP3 and AM35xx voltage-domain objects and wires OMAP3 MPU/core scalable domains to VC/VP data and OPP voltage tables.

### Important APIs, Types, And Functions
It exports `omap3xxx_voltagedomains_init()`. Important objects are `omap3_voltdm_mpu`, `omap3_voltdm_core`, `omap3_voltdm_wkup`, AM35xx non-scalable alternatives, OMAP3 VFSM instances, and the `voltagedomains_omap3`/`voltagedomains_am35xx` lists.

### Control Flow
Init selects OMAP34xx or OMAP36xx OPP voltage data when `CONFIG_PM_OPP` is enabled, assigns VP/VC parameter pointers, selects the AM35xx or normal OMAP3 list, sets each domain's sysclk name to `sys_ck`, and registers the domains.

### State, Persistence, And Dependencies
Static voltage-domain objects persist in the global registry. Scalable OMAP3 domains carry PRM read/write/rmw callbacks, VC channels, VFSM register masks, VP instances, voltage tables, and sysclk names.

### Integration Points
The file links OMAP3-specific voltage data with generic `voltage.c`, `vc.c`, `vp.c`, SmartReflex, and OPP data.

### Risks
AM35xx domains are intentionally non-scalable; code assuming all OMAP3-like platforms have VC/VP will fail. Without `CONFIG_PM_OPP`, voltage tables remain unset and late scaling cannot proceed.

### Test Signals
Boot should register `mpu_iva`, `core`, and `wakeup` on OMAP3, but only non-scalable domains on AM35xx. DVFS/SmartReflex tests should cover OMAP34xx and OMAP36xx voltage tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains3xxx_data.c -->
