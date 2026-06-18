# sources/distributed-fs/ceph-client/include/media/vsp1.h

Purpose: This header defines Renesas R-Car VSP1/VSPX integration APIs for display-unit composition and ISP-assisted transfers. It is a cross-driver interface between VSP hardware drivers, DRM display pipelines, and ISP drivers.

Important APIs, types, and functions: Display-unit APIs include `vsp1_du_init()`, `vsp1_du_setup_lif()`, `vsp1_du_atomic_begin()`, `vsp1_du_atomic_update()`, `vsp1_du_atomic_flush()`, `vsp1_du_map_sg()`, and `vsp1_du_unmap_sg()`. Display structs include `vsp1_du_lif_config`, `vsp1_du_atomic_config`, `vsp1_du_crc_config`, `vsp1_du_writeback_config`, and `vsp1_du_atomic_pipe_config`. ISP APIs include `vsp1_isp_init()`, `vsp1_isp_get_bus_master()`, buffer allocation/free helpers, streaming start/stop, job prepare/run/release, and frame-end callbacks. `struct vsp1_isp_job_desc` describes optional ConfigDMA register pairs, RAW image format and address, and a prepared display-list pointer.

Control flow: A DU client initializes VSP1, configures the LIF, begins an atomic update, submits one plane config per RPF/input, and flushes with optional CRC or writeback config. Completion status is reported through an optional callback exactly once per flush. An ISP client initializes VSPX, allocates buffers through VSP, starts streaming with a frame-end callback, prepares job display lists from config and image descriptors, runs jobs, and releases prepared but unused jobs during stream stop.

State and persistence behavior: The header passes DMA addresses, SG tables, display-list pointers, and callbacks between drivers; persistent hardware state is owned by the implementation. `vsp1_isp_buffer_desc` stores CPU and DMA mappings for allocated buffers. `vsp1_isp_job_desc.dl` is a prepared runtime resource that must be released if not run.

Dependencies and integration points: It depends on scatterlists, DMA addresses, V4L2 rectangles and pixel formats, and V4L2 color metadata. It integrates Renesas DRM DU plane composition, VSP display lists, ISP RAW image transfers, ConfigDMA, CRC capture, writeback, and SG mapping.

Risks: The ConfigDMA comment documents dangerous hardware behavior for fewer than 17 register pairs, including corruption or freeze, so clients must pad or avoid small transfers. Atomic callbacks must be exactly once per flush. DMA address arrays and pixel formats must match plane layout. Prepared jobs leak resources if not run or released. SG map/unmap must be balanced.

Test signals: Atomic plane composition with multiple z positions, interlaced LIF setup, CRC source selection, writeback buffers, SG map/unmap failures, ISP buffer allocation/free, ConfigDMA pair counts below and above the safe threshold, job prepare/run/release ordering, and stream stop with pending jobs.
