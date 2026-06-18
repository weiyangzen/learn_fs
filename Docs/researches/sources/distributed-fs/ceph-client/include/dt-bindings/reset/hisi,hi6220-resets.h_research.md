# sources/distributed-fs/ceph-client/include/dt-bindings/reset/hisi,hi6220-resets.h

Purpose: `hisi,hi6220-resets.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 71 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are PERIPH (58), MEDIA (7), AO_G3D (1), AO_CODECISP (1),
AO_MCPU (1), AO_BBPHARQMEM (1), AO_HIFI (1), AO_ACPUSCUL2C (1). Representative constants are
`PERIPH_RSTDIS0_MMC0`, `PERIPH_RSTDIS0_MMC1`, `PERIPH_RSTDIS0_MMC2`, `PERIPH_RSTDIS0_NANDC`,
`PERIPH_RSTDIS0_USBOTG_BUS`, `PERIPH_RSTDIS0_POR_PICOPHY`, `PERIPH_RSTDIS0_USBOTG`,
`PERIPH_RSTDIS0_USBOTG_32K`, `...`, `MEDIA_MMU`, `MEDIA_XG2RAM1`, `AO_G3D`, `AO_CODECISP`,
`AO_MCPU`, `AO_BBPHARQMEM`, `AO_HIFI`, `AO_ACPUSCUL2C`. Function-like helpers are none. Value shape:
literal numeric range 0..1288 across 71 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_HI6220`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PERIPH group`, `MEDIA group`, `AO_G3D group`, `AO_CODECISP group`, `AO_MCPU group`,
`AO_BBPHARQMEM group`, `AO_HIFI group`, `AO_ACPUSCUL2C group`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 83 lines long. Notable source comments include `This header provides index for the reset
controller based on hi6220 SoC.`, `_DT_BINDINGS_RESET_CONTROLLER_HI6220`. Example value clusters are
PERIPH: `PERIPH_RSTDIS0_MMC0=0x000`, `PERIPH_RSTDIS0_MMC1=0x001`, `PERIPH_RSTDIS0_MMC2=0x002`,
`PERIPH_RSTDIS0_NANDC=0x003`; MEDIA: `MEDIA_G3D=0`, `MEDIA_CODEC_VPU=2`, `MEDIA_CODEC_JPEG=3`,
`MEDIA_ISP=4`; AO_G3D: `AO_G3D=1`; AO_CODECISP: `AO_CODECISP=2`; AO_MCPU: `AO_MCPU=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `PERIPH_RSTDIS0_MMC0`,
`PERIPH_RSTDIS0_MMC1`, `PERIPH_RSTDIS0_MMC2`, `PERIPH_RSTDIS0_NANDC`, `PERIPH_RSTDIS0_USBOTG_BUS`,
`PERIPH_RSTDIS0_POR_PICOPHY`, `PERIPH_RSTDIS0_USBOTG`, `PERIPH_RSTDIS0_USBOTG_32K`. Test signals
include DTS compile checks, reset-controller probe, driver reset/deassert paths, and peripheral
reinitialization after module or runtime-PM cycles.
