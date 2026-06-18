# sources/distributed-fs/ceph-client/include/uapi/linux/media/arm/mali-c55-config.h

Purpose: defines the ARM Mali-C55 ISP userspace ABI for capability controls, 3A statistics buffers, and V4L2 ISP parameter blocks controlling exposure histograms, AWB, digital gain, sensor offsets, and mesh shading.

Important APIs and types: `V4L2_CID_MALI_C55_CAPABILITIES` and `MALI_C55_GPS_*` flags advertise hardware pipeline capabilities. Statistics structs include 1024-bin AE histograms, 5-bin AE zone histograms, AWB average ratios, AF statistics, and aggregate `struct mali_c55_stats_buffer`. `enum mali_c55_param_block_type` selects typed blocks. Parameter structs include sensor black-level offsets, AEXP histogram config, AEXP weights, digital gain, AWB gains/config, mesh shading table config, mesh alpha bank selection, and mesh selection. `MALI_C55_PARAMS_MAX_SIZE` sums the maximum multi-block parameter buffer footprint.

Control flow: userspace queries capabilities, consumes per-frame stats metadata, computes 3A/lens-shading decisions, and submits a buffer of typed `v4l2_isp_params_block_header` blocks. Histogram configuration controls tap points, skip/offset patterns, intensity scaling, plane modes, and zone weights. AWB config gates pixel inclusion by intensity and ratio windows. Mesh shading config uploads coefficient pages and selection blends light-source tables.

State and persistence: stats buffers are frame outputs. Parameter blocks update runtime ISP state: offsets, histograms, digital gain, AWB gains/windows, and mesh tables. Mesh tables can be large runtime state but are not persistent beyond driver/device lifetime unless userspace reloads them.

Dependencies and integration points: depends on `linux/types.h`, `linux/v4l2-controls.h`, and `linux/media/v4l2-isp.h`. Integrates Mali-C55 V4L2 drivers, media request pipelines, libcamera-style 3A, sensor Bayer order handling, WDR/Iridix paths, and ISP metadata capture.

Risks and test signals: risks include packed-stat layout drift, exponent/mantissa decode errors, invalid skip/offset combinations losing color planes, zone bounds, mesh table size and page selection errors, Q-format scaling mistakes, capability mismatch, repeated struct accounting in max-size, and malformed block headers. Test stats buffer ABI size/content, all parameter block types, histogram plane modes, zone weights, AWB ratio windows, mesh upload/select/blend, invalid enum values, max parameter buffer parsing, and request-synchronized frame application.
