<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h

Purpose: declares the core-level helpers shared by command, debug, platform, and codec code.

Important APIs: CSR accessors, coherent DMA alloc/free for core-owned devices, instance lookup by firmware index, and core state setter.

Control/state behavior: callers use these APIs to access memory-mapped core registers, allocate DMA buffers associated with a core device, find live instances during message dispatch, and transition `enum vpu_core_state`.

Dependencies and integration: depends on `struct vpu_core`, `struct vpu_buffer`, `struct vpu_inst`, and `enum vpu_core_state` from `vpu.h`.

Risks and test signals: small header, mostly build-contract risk. Runtime validation is through core probe/boot, DMA allocation/free paths, and message dispatch to active instance IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_core.h -->
