# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/csi_rx_global.h

Purpose: defines shared CSI RX frontend/backend configuration structures and declares per-controller capability arrays.

Important APIs/types/functions: `csi_mipi_packet_type_t` classifies undefined, long, short, and reserved MIPI packet types. `csi_rx_backend_lut_entry_t` stores long/short LUT entries. `csi_rx_backend_cfg_t` combines LUT entries with virtual channel, data type, compression scheme, predictor, and bit index. `csi_rx_frontend_cfg_t` stores active lane count. Extern arrays describe short/long LUT counts, frontend data-lane counts, and backend SID width.

Control flow: no direct flow. Host configuration code uses these structures to prepare CSI receiver frontend/backend programming.

State and persistence: structures are caller-owned runtime config; extern arrays are read-only hardware capabilities defined in `host/csi_rx.c`.

Dependencies and integration: depends on system ID enums such as `N_CSI_RX_BACKEND_ID` and `N_CSI_RX_FRONTEND_ID`. It links CSI RX host wrappers with MIPI backend register programming.

Risks and test signals: capability arrays must match actual hardware IDs. Tests should validate lane/LUT bounds for all three CSI receiver instances and compression/custom packet setup.
