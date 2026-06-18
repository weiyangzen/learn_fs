<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c

### Purpose
`voltagedomains2xxx_data.c` registers minimal OMAP2 voltage-domain names for core and wakeup domains.

### Important APIs, Types, And Functions
It defines static `voltagedomain` objects for `"core"` and `"wakeup"` and exports `omap2xxx_voltagedomains_init()`.

### Control Flow
The init function calls `voltdm_init()` with a null-terminated OMAP2 domain list.

### State, Persistence, And Dependencies
The domains are static and not marked scalable, so they persist only as lookup records without VC/VP behavior. The file depends on the common voltage-domain registry.

### Integration Points
OMAP2 platform init uses this to make voltage-domain names available to other platform code.

### Risks
No register callbacks, PMIC data, or OPP tables are provided, so callers must not expect DVFS scaling through these domains.

### Test Signals
Boot on OMAP2 should register `core` and `wakeup`, and no voltage late-init scaling should be attempted for them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltagedomains2xxx_data.c -->
