<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c

Purpose: Provides the shared vDPA simulator core: common vDPA ops, vringh setup, kthread worker scheduling, IOTLB mapping, reset/suspend/resume, config access, feature negotiation, and cleanup.

Important APIs/functions: Exports `vdpasim_create()` and `vdpasim_schedule_work()`. Implements two ops tables: `vdpasim_config_ops` with incremental `dma_map/dma_unmap`, and `vdpasim_batch_config_ops` with batch `set_map`. Important helpers include `vdpasim_queue_ready()`, `vdpasim_do_reset()`, `vdpasim_work_fn()`, `vdpasim_set_group_asid()`, `vdpasim_bind_mm()`, and `vdpasim_free()`.

Control flow: Frontends pass `vdpasim_dev_attr` to `vdpasim_create()`, which validates requested features, allocates a vDPA device with optional VA support, starts a kthread worker, allocates config/VQ/IOTLB state, initializes identity IOTLB mappings, and returns the typed simulator. Queue ready initializes vringh over guest descriptor/avail/used addresses using VA or IOTLB mode and restores last avail index. Kicks schedule frontend work unless suspended. Reset clears VQs, optionally resets maps, marks IOTLB passthrough, stops running, clears status/features, and increments generation.

State and persistence: `struct vdpasim` owns VQs, worker, bound mm, config buffer, per-AS vhost IOTLBs, passthrough flags, status, generation, negotiated features, running and pending-kick flags, and locks. No disk persistence; block frontend may persist only in memory.

Dependencies and integration points: Uses vDPA core, vringh, vhost IOTLB, kthread workers, DMA map ops, virtio endian helpers, and frontend callbacks for config/work/stats/free. Net and block modules register management devices and call `_vdpa_register_device()`.

Risks: `use_va` binds worker to an mm and requires careful mm lifetime handling. `vdpasim_dma_unmap()` checks passthrough before taking `iommu_lock`, unlike map path, which is a concurrency-sensitive area. Batch and incremental mapping modes expose different ops. Simulator only tracks split-ring state in `set_vq_state()`. Pending kicks while suspended are replayed on resume.

Test signals: Create/delete net and block simulated devices, run with `batch_mapping` on/off and `use_va` on/off, map/unmap IOTLB ranges, bind/unbind mm through vhost, reset with map cleanup, suspend/resume with pending kick, and verify generation increments and worker cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c -->
