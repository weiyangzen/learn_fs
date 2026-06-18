# sources/distributed-fs/ceph-client/include/dt-bindings/power/raspberrypi-power.h

Purpose: `raspberrypi-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 24 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RPI_POWER (24). Representative
constants are `RPI_POWER_DOMAIN_I2C0`, `RPI_POWER_DOMAIN_I2C1`, `RPI_POWER_DOMAIN_I2C2`,
`RPI_POWER_DOMAIN_VIDEO_SCALER`, `RPI_POWER_DOMAIN_VPU1`, `RPI_POWER_DOMAIN_HDMI`,
`RPI_POWER_DOMAIN_USB`, `RPI_POWER_DOMAIN_VEC`, `...`, `RPI_POWER_DOMAIN_CPI`,
`RPI_POWER_DOMAIN_DSI0`, `RPI_POWER_DOMAIN_DSI1`, `RPI_POWER_DOMAIN_TRANSPOSER`,
`RPI_POWER_DOMAIN_CCP2TX`, `RPI_POWER_DOMAIN_CDP`, `RPI_POWER_DOMAIN_ARM`, `RPI_POWER_DOMAIN_COUNT`.
Function-like helpers are none. Value shape: literal numeric range 0..23 across 24 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_ARM_BCM2835_RPI_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RPI_POWER group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 38 lines long. Notable source comments include `These power domain indices are the
firmware interface's indices minus one.`, `_DT_BINDINGS_ARM_BCM2835_RPI_POWER_H`. Example value
clusters are RPI_POWER: `RPI_POWER_DOMAIN_I2C0=0`, `RPI_POWER_DOMAIN_I2C1=1`,
`RPI_POWER_DOMAIN_I2C2=2`, `RPI_POWER_DOMAIN_VIDEO_SCALER=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPI_POWER_DOMAIN_I2C0`, `RPI_POWER_DOMAIN_I2C1`, `RPI_POWER_DOMAIN_I2C2`,
`RPI_POWER_DOMAIN_VIDEO_SCALER`, `RPI_POWER_DOMAIN_VPU1`, `RPI_POWER_DOMAIN_HDMI`,
`RPI_POWER_DOMAIN_USB`, `RPI_POWER_DOMAIN_VEC`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
