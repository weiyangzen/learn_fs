# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys_comm.h

Purpose: shared communication definitions for virtual input-system stream handles/configs and stream IDs.

Important types/macros: `SH_CSS_NODES_PER_THREAD`, `SH_CSS_MAX_ISYS_CHANNEL_NODES`, `ia_css_isys_stream_h`, `ia_css_isys_stream_cfg_t`, `ia_css_isys_error_t`, and inline `ia_css_isys_generate_stream_id(sp_thread_id, stream_id)`.

Control flow/state: no owned state. The stream ID formula maps SP thread plus per-channel stream id into a flat CSI RX tracking bit index.

Dependencies/integration: relies on `input_system.h`, `input_system_global.h`, platform inline support, and `IA_CSS_STREAM_MAX_ISYS_STREAM_PER_CH`. `csi_rx_rmgr.c` validates IDs against `SH_CSS_MAX_ISYS_CHANNEL_NODES`.

Risks: stream ID generation has no bounds check; callers must ensure both components fit the maximum node count. The comment notes handles are concrete structs because SP must interpret them, making layout an ABI concern.

Test signals: stream ID uniqueness across threads/channels, maximum boundary validation in register/unregister, and ABI build checks for virtual stream structs.
