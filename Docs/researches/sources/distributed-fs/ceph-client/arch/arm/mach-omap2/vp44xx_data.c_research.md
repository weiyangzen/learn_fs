<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c

### Purpose
`vp44xx_data.c` defines OMAP4 Voltage Processor metadata for MPU, IVA, and CORE voltage domains.

### Important APIs, Types, And Functions
It defines `omap4_vp_ops`, `omap4_vp_common`, `omap4_vp_mpu`, `omap4_vp_iva`, `omap4_vp_core`, and `omap4_{mpu,iva,core}_vp_data`.

### Control Flow
The file is declarative. Generic VP code reads these objects when initializing and scaling OMAP4-class voltage domains.

### State, Persistence, And Dependencies
VP instances persist and track enabled state. Dependencies include OMAP4 PRM offsets, VP bit masks, and common PRM VP transaction-done helpers.

### Integration Points
OMAP4 voltage-domain data uses these directly, and OMAP5 voltage-domain data reuses them for compatible domains.

### Risks
Reusing these objects for OMAP5 means register compatibility assumptions must hold. Min/max limits are static OMAP4 values and may need SoC-specific review for derivatives.

### Test Signals
OMAP443x/446x DVFS should exercise all three VP instances and validate transaction-done status for MPU, IVA, and CORE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp44xx_data.c -->
