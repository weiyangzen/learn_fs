# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.c

Purpose: manages CSI RX backend LUT entries and tracks active virtual streams per MIPI port.

Important functions/state: static `isys_csi_rx_rsrc[N_CSI_RX_BACKEND_ID]`; init/uninit clear it. `ia_css_isys_csi_rx_lut_rmgr_acquire/release` allocates long/short packet LUT slots using a bitmap and counters. `ia_css_isys_csi_rx_register_stream/unregister_stream` set/clear bits in `sh_css_sp_group.pipe_io_status`.

Control flow: LUT acquire checks backend, packet type, and capacity, then finds the first free bit, fills either long or short entry, and increments active counters. Release clears matching bits and counters if the entry is valid and active.

State/persistence: backend resource tables and SP pipeline I/O status persist globally; no locking is present.

Dependencies/integration: bit operations, `ia_css_pipeline_get_pipe_io_status`, `sh_css_internal` limits, and CSI RX hardware constants.

Risks: resource manager is not thread-safe. The release assertion for packet type uses `||` semantics and is weaker than intended. Long and short packets share one active bitmap indexed from zero, so correctness depends on hardware LUT ranges and counters.

Test signals: allocate to capacity for long and short entries, release/reacquire reuse, invalid duplicate stream register/unregister, and concurrent stream setup serialization.
