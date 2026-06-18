# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3576-power.h

Purpose: `rockchip,rk3576-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3576 (19). Representative
constants are `RK3576_PD_NPU`, `RK3576_PD_NPUTOP`, `RK3576_PD_NPU0`, `RK3576_PD_NPU1`,
`RK3576_PD_GPU`, `RK3576_PD_NVM`, `RK3576_PD_SDGMAC`, `RK3576_PD_USB`, `...`, `RK3576_PD_VEPU0`,
`RK3576_PD_VEPU1`, `RK3576_PD_VPU`, `RK3576_PD_VDEC`, `RK3576_PD_VI`, `RK3576_PD_VO0`,
`RK3576_PD_VO1`, `RK3576_PD_VOP`. Function-like helpers are none. Value shape: literal numeric range
0..18 across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3576_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_NPU`, `VD_GPU`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 30 lines long. Notable source comments include `VD_NPU`, `VD_GPU`, `VD_LOGIC`. Example
value clusters are RK3576: `RK3576_PD_NPU=0`, `RK3576_PD_NPUTOP=1`, `RK3576_PD_NPU0=2`,
`RK3576_PD_NPU1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3576_PD_NPU`, `RK3576_PD_NPUTOP`, `RK3576_PD_NPU0`, `RK3576_PD_NPU1`, `RK3576_PD_GPU`,
`RK3576_PD_NVM`, `RK3576_PD_SDGMAC`, `RK3576_PD_USB`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
