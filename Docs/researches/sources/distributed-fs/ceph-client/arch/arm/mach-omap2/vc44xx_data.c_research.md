<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c

### Purpose
`vc44xx_data.c` provides OMAP4 Voltage Controller metadata for MPU, IVA, and CORE voltage channels plus default voltage command parameters.

### Important APIs, Types, And Functions
It defines `omap4_vc_common`, `omap4_vc_mpu`, `omap4_vc_iva`, `omap4_vc_core`, and `omap4_{mpu,iva,core}_vc_data`.

### Control Flow
The file is declarative; `vc.c` uses the exported structures when voltage-domain late init configures VC channels.

### State, Persistence, And Dependencies
The VC channel structures persist and receive PMIC runtime fields. Dependencies are OMAP4 PRM offsets and bitfield masks from `prm44xx.h` and `prm-regbits-44xx.h`.

### Integration Points
OMAP4 and OMAP5 voltage-domain data reuse these VC channel definitions.

### Risks
The MPU channel is flagged as both default and mutant, reflecting nonstandard channel bit layout; clearing or misusing those flags would program the wrong channel fields. The default off voltage is zero, which relies on PMIC support and correct board scripts.

### Test Signals
Register dumps on OMAP443x/446x should show channel-specific PMIC addresses and command values in the expected PRM offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc44xx_data.c -->
