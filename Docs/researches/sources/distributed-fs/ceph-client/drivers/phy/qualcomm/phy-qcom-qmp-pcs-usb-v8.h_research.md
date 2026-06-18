# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-usb-v8.h

Purpose: Defines the QMP v8 USB PCS register offsets for USB-specific power-state, LFPS, receiver-detect, RX equalization training, and test-control programming. It is a narrow address-map header, not an implementation file.

Important APIs/types/functions: Exports `QPHY_V8_PCS_USB_*` macros, including `POWER_STATE_CONFIG1..4`, `AUTONOMOUS_MODE_*`, `LFPS_*`, `RXEQTRAINING_*`, `RCVR_DTCT_*`, and `TEST_CONTROL`. There are no functions or types.

Control flow: No executable control flow exists. Runtime flow is indirect through QMP USB/combo init arrays that use these macros in `QMP_PHY_INIT_CFG` entries before the generic QMP PHY start and status polling sequence.

State and persistence: The header has no mutable state. Values written through these offsets persist in USB PCS hardware until reset, power collapse, or a later reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp-usb.c` and `phy-qcom-qmp-combo.c`; used with common QMP register write helpers.

Risks: Wrong offsets can silently program LFPS or power-state registers incorrectly, causing USB3 link training, U1/U2/U3 transitions, or receiver detect failures.

Test signals: Build coverage for v8 USB PHY tables, probe on matching Qualcomm platforms, USB3 link-up, suspend/resume, LFPS wake, and link-training stability.
