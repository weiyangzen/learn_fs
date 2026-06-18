# sources/distributed-fs/ceph-client/include/linux/host1x.h

## Purpose
`host1x.h` defines the public interface for NVIDIA Tegra host1x clients, buffer objects, syncpoints, channels, jobs, logical host1x devices, and memory contexts. It is used by DRM/media/accelerator drivers that submit command streams through host1x engines.

## Important APIs, Types, And Functions
Core types include `enum host1x_class`, `struct host1x_client`, `struct host1x_client_ops`, `struct host1x_bo`, `struct host1x_bo_mapping`, `struct host1x_bo_ops`, `struct host1x_syncpt`, `struct host1x_channel`, `struct host1x_job`, `struct host1x_reloc`, `struct host1x_driver`, `struct host1x_device`, and `struct host1x_memory_context`. Public APIs cover DMA mask lookup, BO cache init/destroy, BO pin/unpin/mmap, syncpoint lookup/read/increment/wait/alloc/request/fence creation, channel request/get/stop/put, job allocation/add gather/add wait/get/put/pin/unpin/submit, host1x driver registration, client registration/suspend/resume, device init/exit, and IOMMU-backed memory context allocation/reference management.

## Control Flow And State
Client drivers initialize/register `host1x_client`, request channels and syncpoints, allocate jobs, add command gathers/relocations/waits, pin buffer objects, submit jobs, and track completion through syncpoints and DMA fences. BO mappings may be cached until explicitly released. Logical devices group subdevices and clients. Memory contexts provide stream IDs for engine isolation when IOMMU support is enabled. State persists in client use counts/locks/cache, BO mapping refs and DMA addresses, job refs/fences/pinned buffers, syncpoint thresholds, and device client lists.

## Dependencies And Integration Points
It depends on Linux device model, DMA direction/fence APIs, spinlocks/mutexes/krefs/refcounts, IOMMU groups, OF IDs, and DMA-buf attachments. It integrates Tegra DRM/KMS, media engines, IOMMU context bus, and scheduler/fence users.

## Risks
Risks include BO mapping cache leaks, refcount imbalance, stale DMA mappings, relocation validation/firewall bypass, syncpoint timeout/recovery mistakes, job cancellation races, IOMMU stream ID misprogramming, and client registration double-initialization. The BO cache is not automatically evicted, so owners must release cached mappings.

## Test Signals
Test client probe/remove, multi-engine logical devices, job submit/completion/timeout, syncpoint waits and fences, BO pin/unpin cache reuse and teardown, relocation firewall validation, suspend/resume, memory context allocation with and without IOMMU, and DMA API debug.
