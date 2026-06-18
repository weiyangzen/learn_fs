# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c

This file provides GFX10 DQM ASIC callbacks. It adapts generic DQM behavior to Navi-era SH_MEM register layout, MQD creation, and SDMAv4+ behavior.

`device_queue_manager_init_v10` installs `set_cache_memory_policy_v10`, `update_qpd_v10`, `init_sdma_vm_v10`, and `mqd_manager_init_v10`. `compute_sh_mem_bases_64bit` derives shared and private SH_MEM bases from `pdd->lds_base` and `pdd->scratch_base`. `set_cache_memory_policy_v10` sets unaligned SH_MEM mode, initial instruction prefetch value `3`, disables APE1, and records computed bases. `update_qpd_v10` is a no-op. `init_sdma_vm_v10` sets `sdma_vm_addr` to zero because SDMAv4+ no longer needs explicit SDMA VM aperture programming.

The callbacks are invoked during process registration, cache-policy handling, and SDMA queue creation. State lives in QPD SH_MEM fields and queue properties; no independent file-local state persists. GFX10 does not implement the per-process XNACK update logic found in GFX9/GFX12.1.

Dependencies include GFX10 register masks, `mqd_manager_init_v10`, and aperture setup from `kfd_flat_memory.c`. It is selected for GC versions from 10.1.1 to below GFX11. Risks are SH_MEM base extraction drift, missing prefetch programming, and assuming SDMA VM address stays unused. Test queue creation, cache policy ioctls, SDMA/XGMI SDMA queues, MES and runlist scheduling, and flat LDS/scratch workloads.
