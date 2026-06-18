# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_local.h

Purpose: defines local state snapshot structures for CSI RX frontend and backend controllers.

Important APIs/types/functions: `csi_rx_fe_ctrl_lane_t` stores `termen` and `settle`. `csi_rx_fe_ctrl_state_t` captures frontend enable, lane count, error handling, status, lane status, clock lane, and data lanes. `csi_rx_be_ctrl_state_t` captures backend enable/status, compression registers, raw16/raw18/force-raw8 controls, IRQ status, custom-mode fields, LUT disregard/stall status, and short/long packet LUT entries.

Control flow: none in the header. Private helpers fill these structures from MMIO registers and dump them.

State and persistence: snapshot-only runtime state; not persistent and not authoritative for hardware.

Dependencies and integration: depends on `csi_rx_global.h` capability constants and HRT data types.

Risks and test signals: fixed array sizes must cover maximum hardware counts. State dump tests should verify backend0 long LUT entries do not exceed `N_CSI_RX_BE_LONG_PACKET_LUT` and disabled custom registers remain handled.
