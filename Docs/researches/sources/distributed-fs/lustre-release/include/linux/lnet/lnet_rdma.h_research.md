# sources/distributed-fs/lustre-release/include/linux/lnet/lnet_rdma.h

Purpose: RDMA/GPU-direct integration header for LNet. It defines or imports NVFS DMA hooks and exposes LNet wrappers for device priority, scatterlist mapping, and GPU page detection.

Important APIs/types: when `WITH_EXTERNAL_GDS_HEADER` is not set, it defines `struct nvfs_dma_rw_ops` with callbacks for block request SG mapping, DMA map/unmap, GPU page detection, GPU index, and device priority. Feature bits and `NVIDIA_FS_CHECK_FT_*` macros advertise supported operations. Symbol-generation macros create versioned registration names `lustre_v1_register_nvfs_dma_ops` and `lustre_v1_unregister_nvfs_dma_ops`. LNet wrappers include `lnet_get_dev_prio`, `lnet_rdma_map_sg_attrs`, `lnet_rdma_unmap_sg`, `lnet_is_rdma_only_page`, and `lnet_get_dev_idx`.

Control flow: vendor/driver code registers an operations table; LNet checks feature bits and routes DMA mapping/unmapping or GPU page classification through registered callbacks, falling back to CPU paths when unavailable.

State and persistence: runtime registration state is external to this header and volatile.

Dependencies/integration: depends on Linux DMA, block, scatterlist, cpumask, and page APIs. It integrates Lustre networking with NVIDIA GPUDirect Storage style hooks.

Risks and test signals: risks include stale external header ABI, missing feature bits, wrong DMA direction, unbalanced map/unmap, and GPU-page misclassification. Test signals are registration/unregistration, CPU fallback, GPU page send/receive paths, DMA_ATTR_NO_WARN compatibility, and device priority selection.
