# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com.h

Purpose: Provides the original/base QSERDES common register map used by early QMP PHY drivers. It defines PLL, SSC, clock, lock, reset, VCO, SAR, debug, and reserved common-block offsets.

Important APIs/types/functions: Exports `QSERDES_COM_*` macros for `SSC_*`, `CLK_EP_DIV`, `CP_CTRL`, `PLL_RCTRL`, `PLL_CCTRL`, `LOCK_CMP*`, `DEC_START`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `SYS_CLK_CTRL`, `PLL_IVCO`, `RESETSM_*`, `LOCK_CMP_EN`, `SAR`, `DEBUG_BUS*`, `CMN_RSVD*`, and many related controls. No functions or structs.

Control flow: None. Included by the umbrella QMP header and used in static init tables executed by protocol drivers.

State and persistence: Stateless constants. Hardware common/PLL state is persistent only after register writes and until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by legacy QMP USB/PCIe/UFS configurations.

Risks: This base namespace lacks a version suffix. New table authors must not assume it applies to newer QSERDES versions.

Test signals: Compile for legacy users, PLL lock, protocol link-up, SSC/clock behavior, and resume.
