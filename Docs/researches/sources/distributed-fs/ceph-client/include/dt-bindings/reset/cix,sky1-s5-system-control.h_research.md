# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-s5-system-control.h

Purpose: `cix,sky1-s5-system-control.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 143 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SKY1 (143). Representative constants are
`SKY1_CSU_PM_RESET_N`, `SKY1_SENSORFUSION_RESET_N`, `SKY1_SENSORFUSION_NOC_RESET_N`,
`SKY1_DDRC_RESET_N`, `SKY1_GIC_RESET_N`, `SKY1_CI700_RESET_N`, `SKY1_SYS_NI700_RESET_N`,
`SKY1_MM_NI700_RESET_N`, `...`, `SKY1_RCSU_USB2_HOST2_RESET_N`, `SKY1_RCSU_USB2_HOST3_RESET_N`,
`SKY1_RCSU_USB3_TYPEA_DRD_RESET_N`, `SKY1_RCSU_USB3_TYPEC_DRD_RESET_N`,
`SKY1_RCSU_USB3_TYPEC_HOST0_RESET_N`, `SKY1_RCSU_USB3_TYPEC_HOST1_RESET_N`,
`SKY1_RCSU_USB3_TYPEC_HOST2_RESET_N`, `SKY1_VPU_RCSU_RESET_N`. Function-like helpers are none. Value
shape: literal numeric range 0..142 across 143 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_CIX_SKY1_S5_SYSTEM_CONTROL_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `reset for csu_pm`, `reset group0 for s0 domain modules`, `reset group1 for s0 domain
modules`, `reset group1 for usb phys`, `reset group1 for usb controllers`, `reset group0 for rcsu`,
`reset group1 for rcsu`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 163 lines long. Notable source comments include `reset for csu_pm`, `reset group0 for s0
domain modules`, `reset group1 for s0 domain modules`, `reset group1 for usb phys`, `reset group1
for usb controllers`, `reset group0 for rcsu`. Example value clusters are SKY1:
`SKY1_CSU_PM_RESET_N=0`, `SKY1_SENSORFUSION_RESET_N=1`, `SKY1_SENSORFUSION_NOC_RESET_N=2`,
`SKY1_DDRC_RESET_N=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SKY1_CSU_PM_RESET_N`,
`SKY1_SENSORFUSION_RESET_N`, `SKY1_SENSORFUSION_NOC_RESET_N`, `SKY1_DDRC_RESET_N`,
`SKY1_GIC_RESET_N`, `SKY1_CI700_RESET_N`, `SKY1_SYS_NI700_RESET_N`, `SKY1_MM_NI700_RESET_N`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
