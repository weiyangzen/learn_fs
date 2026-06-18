# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp.h

Purpose: Aggregates Qualcomm QMP QSERDES and PCS register definition headers and defines common bit masks used by multiple QMP PHY drivers.

Important APIs/types/functions: This header exports no functions or structs. It includes versioned COM, TXRX, lane-shared, PLL, and PCS register headers, then defines shared bits such as `SW_RESET`, `SW_PWRDN`, `REFCLK_DRV_DSBL`, `SERDES_START`, `PCS_START`, `PHYSTATUS`, autonomous-mode interrupt bits, `IRQ_CLEAR`, and `CLAMP_EN`.

Control flow: There is no executable control flow. Including drivers use these symbols while building their power, reset, start, status, and low-power register sequences.

State and persistence: The file has no mutable state. The constants become persistent only when a consumer writes them to hardware registers.

Dependencies and integration points: It is a compile-time integration point between QMP driver source files and the register definition headers under `drivers/phy/qualcomm`. Consumers include USB, PCIe, UFS, and USB-C QMP drivers that need common state-machine bits independent of QSERDES generation.

Risks: This is a central include surface. Renaming or changing a bit definition can silently alter hardware sequencing across several PHY drivers. Because included headers cover many hardware generations, include-order conflicts or duplicated register names are a build-time risk.

Test signals: Compile all Qualcomm QMP PHY drivers, boot/probe a representative USB/PCIe/UFS QMP PHY, and verify reset, start, status polling, and autonomous-mode suspend paths still program expected bit values.
