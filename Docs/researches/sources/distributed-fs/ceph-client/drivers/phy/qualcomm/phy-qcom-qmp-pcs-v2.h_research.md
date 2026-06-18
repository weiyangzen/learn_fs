# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v2.h

Purpose: Provides the legacy QMP v2 PCS register map shared by early USB and PCIe PHY configurations. It covers reset/start, power state, lock detect, FLL, LFPS, signal-detect, wake-delay, and status offsets.

Important APIs/types/functions: Exports `QPHY_V2_PCS_*` macros such as `SW_RESET`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `FLL_*`, `USB_PCS_STATUS`, and `PCI_PCS_STATUS`. No functions or data structures are defined.

Control flow: No code executes here. The common QMP header includes it, and protocol drivers reference the constants from static init tables consumed by the QMP PHY initialization sequence.

State and persistence: The macros identify hardware registers; runtime state is only created when the driver writes or polls those addresses. Hardware settings persist until the PHY is reset or powered down.

Dependencies and integration points: Pulled into `phy-qcom-qmp.h`, then used by QMP USB/PCIe-era SoC tables.

Risks: v2 has USB and PCIe status offsets in the same PCS map, so using the wrong protocol-specific status macro can break readiness detection.

Test signals: Compile use of v2 tables, successful probe, PLL/PCS lock polling, USB/PCIe link establishment, and low-power wake timing.
