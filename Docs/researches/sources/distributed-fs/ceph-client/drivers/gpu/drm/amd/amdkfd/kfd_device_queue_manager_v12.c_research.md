# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c

This file provides GFX12.0 DQM ASIC callbacks for SOC24-class devices, keeping the SH_MEM and SDMAv4+ model used by GFX10/GFX11.

`device_queue_manager_init_v12` installs `set_cache_memory_policy_v12`, `update_qpd_v12`, `init_sdma_vm_v12`, and `mqd_manager_init_v12`. `compute_sh_mem_bases_64bit` derives shared/private SH_MEM fields from process LDS and scratch bases. `set_cache_memory_policy_v12` programs unaligned alignment, initial instruction prefetch `3`, disabled APE1, and computed SH_MEM bases. `update_qpd_v12` is a no-op. `init_sdma_vm_v12` clears `sdma_vm_addr`.

Generic DQM selects this implementation for GC 12.0.x below 12.1. It does not store file-local state; it mutates QPD and queue-property fields consumed by generic queue creation, packet-manager runlists, MQD managers, and MES.

Dependencies include `gc_12_0_0_sh_mask.h`, `soc24_enum.h`, `mqd_manager_init_v12`, and `kfd_flat_memory.c` aperture setup. Risks include GC12 register layout drift and the broader device-layer note that GFX12.0 event interrupts still use a v11 class pending a future v12 handler. Test GFX12.0 queue creation, MES/non-MES paths where available, SH_MEM dumps, SDMA queues, flat-memory tests, and cache policy compatibility.
