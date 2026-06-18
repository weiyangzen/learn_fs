<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h

### Purpose
`vp.h` defines the OMAP Voltage Processor metadata model, operation callbacks, timeout constants, exported SoC instances, and VP API prototypes.

### Important APIs, Types, And Functions
Key types are `struct omap_vp_ops`, `struct omap_vp_common`, and `struct omap_vp_instance`. It declares OMAP3/4 VP instances and parameters plus `omap_vp_init()`, `omap_vp_enable()`, `omap_vp_disable()`, `omap_vp_forceupdate_scale()`, and `omap_vp_update_errorgain()`.

### Control Flow
The header has no runtime flow; it describes the register offsets, bit masks, and status callbacks used by `vp.c`.

### State, Persistence, And Dependencies
Each `omap_vp_instance` carries a persistent `enabled` flag and per-domain register offsets. The header depends on voltage-domain declarations and SoC-specific data definitions.

### Integration Points
Voltage-domain data points to these VP instances, and SmartReflex/voltage scaling code calls the declared operations.

### Risks
Wrong masks or shifts can corrupt VP register fields. Timeout constants are global, not per-PMIC or per-SoC.

### Test Signals
Build coverage across OMAP3 and OMAP4 validates declarations; runtime register and DVFS tests validate offsets and masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.h -->
