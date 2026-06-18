<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h

Purpose: defines Marvell Octeon CN10K DPI ioctl payloads for configuring PCIe MPS/MRRS and DPI engine FIFO/outstanding-load parameters.

Important APIs and types: `DPI_MAX_ENGINES` is six. `struct dpi_mps_mrrs_cfg` carries max read request size, max payload size, and EBUS port. `struct dpi_engine_cfg` carries FIFO mask, per-engine maximum outstanding load requests, update flag, and reserved field. Ioctls `DPI_MPS_MRRS_CFG` and `DPI_ENGINE_CFG` use magic `0xB8`.

Control flow, state, and persistence: privileged userspace sends configuration ioctls to tune DPI hardware behavior. Settings persist in device registers until changed or reset.

Dependencies and integration points: integrates the CN10K DPI driver, PCIe transaction sizing, DMA engines, and platform tuning tools.

Risks and test signals: risks include invalid MPS/MRRS values, port mismatch, FIFO mask interpretation, and partial engine updates. Test ioctl validation, all engine indexes, reset defaults, performance counters, and invalid reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h -->
