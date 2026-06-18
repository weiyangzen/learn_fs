# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-pcs-v8.h

## Purpose

This header defines USB4.3 v8 QMP PCS register offsets. It has no executable logic; it is a register-map contract used by table-driven Qualcomm QMP PHY drivers that need USB4.3-specific PCS offsets.

The header is included indirectly through the broader QMP register header stack and is used by USB4.3/DP combo PHY data, notably in `phy-qcom-qmp-combo.c`. The standalone USB3 driver in this work item uses `QPHY_V8_PCS_*` names for Glymur USB3 UNI PHY rather than these `QPHY_V8_USB43_PCS_*` names.

## Important APIs, types, and data

- Include guard: `QCOM_PHY_QMP_USB43_PCS_V8_H_`.
- The file exports preprocessor constants only.
- Register groups include:
  - Core control/status: `QPHY_V8_USB43_PCS_SW_RESET`, `QPHY_V8_USB43_PCS_PCS_STATUS1`, `QPHY_V8_USB43_PCS_POWER_DOWN_CONTROL`, and `QPHY_V8_USB43_PCS_START_CONTROL`.
  - Power and lock-detection tuning: `POWER_STATE_CONFIG1`, `LOCK_DETECT_CONFIG1/2/3/6`, and `REFGEN_REQ_CONFIG1`.
  - Receiver detect and synchronization: `RX_SIGDET_LVL`, `RCVR_DTCT_DLY_P1U2_L/H`, `RATE_SLEW_CNTRL1`, `TSYNC_RSYNC_TIME`, `RX_CONFIG`, and `TSYNC_DLY_TIME`.
  - Alignment and equalization: `ALIGN_DETECT_CONFIG1/2`, `PCS_TX_RX_CONFIG`, `EQ_CONFIG1/2/5`.

## Control flow

There is no control flow in this header. Consumers use these macros inside initialization tables, register-layout arrays, or direct MMIO accessors. The usual flow is that a driver selects a compatible-specific table, then common QMP helpers write values at these offsets relative to the mapped PCS base.

## State and persistence behavior

The header stores no state. The defined offsets name hardware registers whose values persist only according to PHY power/reset behavior. Any persistence semantics are determined by the consuming driver and the PHY hardware.

## Dependencies and integration points

- Consumed by Qualcomm QMP PHY C files through `#include "phy-qcom-qmp.h"` or direct includes.
- Depends on the v8 USB4.3 hardware register layout matching these offsets.
- Integrates with `qmp_phy_init_tbl` arrays and QMP helpers such as `qmp_configure()` in consuming drivers.

## Risks and edge cases

- Offset errors are severe because all table writes using the macro silently target the wrong hardware register.
- The names are USB4.3-specific. Mixing them with non-USB43 v8 PCS macros can be wrong even when numeric ranges look similar.
- Since the header has no compile-time validation against hardware, review must compare against vendor register documentation or known-good downstream tables.

## Test signals

- Compile-time signal: all consumers build with these macro names resolved.
- Runtime signal: USB4.3/DP PHY init reaches PCS-ready/PHY-status completion and links at expected rates.
- Regression tests should cover every consuming compatible that uses `QPHY_V8_USB43_PCS_*` constants, especially after adding or renumbering offsets.
