# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.h

Purpose: Shared internal header for the Tegra VDE driver. It defines register offsets, hardware alignment constants, core device/context/buffer structures, SoC format descriptors, and cross-file function prototypes for V4L2, H.264 decode, IOMMU, DMABUF cache, and platform code.

Important APIs, types, and functions: Register constants cover BSE command queue/control/interrupt fields and hardware buffer alignment (`BSEV_ALIGN`, `FRAMEID_ALIGN`, `SXE_BUFFER`, `VDE_ATOM`). `struct tegra_video_frame` describes decoded/reference frame addresses and metadata. `struct tegra_coded_fmt_desc` binds a coded fourcc to frame-size limits, decoded formats, and decode callbacks. `struct tegra_vde_soc` carries per-SoC capabilities. `struct tegra_vde_bo`, `struct tegra_vde`, `struct tegra_ctx`, and `struct tegra_m2m_buffer` define persistent device, filehandle, and vb2 buffer state. `vb_to_tegra_buf()` converts vb2 buffers to driver buffers.

Control flow: The header itself has no runtime control flow, but it defines the contracts used by the runtime path: V4L2 queues store `tegra_m2m_buffer`; `decode_run()`/`decode_wait()` operate on `tegra_ctx`; platform code allocates `tegra_vde_bo`; IOMMU and DMABUF helpers map buffers before hardware programming; register helpers provide tracing-aware MMIO access.

State and persistence behavior: `tegra_vde` is the long-lived platform device state and includes MMIO bases, locks, completion, IOMMU state, IRAM, secure BO, V4L2/media devices, workqueue, and a DPB-sized `frames` array. `tegra_ctx` is per-open and stores the active H.264 controls and formats. `tegra_m2m_buffer` is per-buffer and stores DMA/IOMMU addresses, attachments, auxiliary BO, and B-frame marker.

Dependencies and integration points: Pulls in Linux completion, DMA direction, IOVA, list/mutex/workqueue, and media/V4L2/videobuf2 headers. It links platform code (`vde.c`), V4L2 code (`v4l2.c`), H.264 decode implementation, IOMMU implementation, and DMABUF cache implementation.

Risks: The structs encode ownership boundaries; misuse can leak IOVA, SG tables, DMABUF attachments, or auxiliary BOs. Flexible array `ctrls[]` requires allocation with enough elements. The register-base-name helper is used for diagnostics and must stay in sync with MMIO fields. Alignment constants are part of ABI-adjacent buffer validation because userspace-provided planes are accepted or rejected based on them.

Test signals: Compile coverage should include all translation units that include this header. Static analysis should verify flexible-array allocation and container conversions. Runtime decode tests indirectly validate `frames`, per-buffer DMA address bookkeeping, and SoC descriptor callbacks. Tracepoint tests can check `tegra_vde_reg_base_name()` labels.
