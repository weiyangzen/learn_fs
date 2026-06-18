<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c

### Purpose
`vc3xxx_data.c` supplies OMAP3 Voltage Controller register metadata, MPU/core channel instances, and default sleep/off voltage parameters.

### Important APIs, Types, And Functions
It defines `omap3_vc_common`, `omap3_vc_mpu`, `omap3_vc_core`, `omap3_mpu_vc_data`, and `omap3_core_vc_data`.

### Control Flow
There is no active flow. Generic VC code consumes these objects during voltage-domain late init.

### State, Persistence, And Dependencies
The channel structures are mutable because `vc.c` fills runtime PMIC addresses and channel config bits. The file depends on OMAP3 PRM register offsets and bit masks.

### Integration Points
OMAP3 voltage-domain data references these channel and parameter objects for `mpu_iva` and `core`.

### Risks
Default voltages are board/PMIC-sensitive and may not match every product. Register metadata must align with OMAP34xx/36xx PRM layout.

### Test Signals
OMAP3 boot should initialize both VC channels, produce expected PRM_VC register values, and scale MPU/core domains correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc3xxx_data.c -->
