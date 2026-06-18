<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c

### Purpose
`vp3xxx_data.c` supplies OMAP3 Voltage Processor register metadata, MPU/core VP instances, and min/max voltage limits.

### Important APIs, Types, And Functions
It defines `omap3_vp_ops`, `omap3_vp_common`, `omap3_vp_mpu`, `omap3_vp_core`, `omap3_mpu_vp_data`, and `omap3_core_vp_data`.

### Control Flow
There is no active flow. Generic VP code consumes these structures during OMAP3 voltage-domain late init.

### State, Persistence, And Dependencies
VP instances persist and hold runtime `enabled` state. The file depends on OMAP3 PRM register offsets, bitfield definitions, and `omap_prm_vp_check_txdone`/`omap_prm_vp_clear_txdone` callbacks.

### Integration Points
OMAP3 voltage-domain data attaches these objects to MPU and core domains.

### Risks
Voltage limits must align with silicon and PMIC capabilities; generic VP init clamps against PMIC limits but bad values still affect safe operating range.

### Test Signals
OMAP3 DVFS should program VP1 and VP2 registers with expected bounds and transaction-done callbacks should work for both IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp3xxx_data.c -->
