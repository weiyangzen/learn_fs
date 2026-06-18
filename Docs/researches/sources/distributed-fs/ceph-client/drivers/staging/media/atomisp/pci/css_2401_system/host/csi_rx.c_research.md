# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx.c

Purpose: defines hardware capability arrays for CSS 2401 CSI RX frontend/backend instances.

Important APIs/types/functions: constants are `N_SHORT_PACKET_LUT_ENTRIES`, `N_LONG_PACKET_LUT_ENTRIES`, `N_CSI_RX_FE_CTRL_DLANES`, and `N_CSI_RX_BE_SID_WIDTH`.

Control flow: no runtime control flow beyond static initialization. Consumers index these arrays by frontend/backend ID.

State and persistence: read-only global constants. They persist for module lifetime.

Dependencies and integration: includes `system_global.h` and `csi_rx_global.h`; used by private state-dump/access helpers and CSI configuration code.

Risks and test signals: incorrect counts cause out-of-range register reads/writes or missing LUT programming. Tests should cover all backend IDs, especially backend0's larger long-packet LUT and three-bit SID width.
