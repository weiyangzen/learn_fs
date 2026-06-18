# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v5.h

Purpose: Supplies the QSERDES v5 common register map for newer QMP PHY PLL and clock programming, including additional mode, miscellaneous, and reserved fields.

Important APIs/types/functions: Exports `QSERDES_V5_COM_*` macros for SSC, clock dividers, charge pump, PLL R/C controls, core-clock dividers, lock compare, dec/div-frac programming, high-speed clock select, integration loop, VCO tune, bias/clock enables, reset state machine, common config, VCO DC level, and `RESERVED_1`. No functions or structs.

Control flow: None locally. Init arrays write these offsets before the common driver starts the PHY and checks lock/readiness.

State and persistence: The header is stateless; hardware PLL/common state persists while powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-sgmii-eth.c`; used by QMP USB/PCIe/UFS/SGMII-related tables.

Risks: v5 is reused across protocols. A value appropriate for one protocol/rate can be invalid for another even though the macro name compiles.

Test signals: Build, PLL lock, protocol link-up, SGMII/USB/PCIe/UFS rate-specific validation, and suspend/resume.
