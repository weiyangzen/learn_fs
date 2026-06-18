# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c

This file supplies GFX11/SOC21 DQM ASIC callbacks. It follows the GFX10 pattern with GFX11 register masks and MQD manager selection.

`device_queue_manager_init_v11` installs `set_cache_memory_policy_v11`, `update_qpd_v11`, `init_sdma_vm_v11`, and `mqd_manager_init_v11`. `compute_sh_mem_bases_64bit` combines `lds_base >> 48` and `scratch_base >> 48` into `SH_MEM_BASES`. `set_cache_memory_policy_v11` programs unaligned alignment, initial instruction prefetch `3`, disabled APE1, and SH_MEM bases. `update_qpd_v11` is a no-op. `init_sdma_vm_v11` clears `sdma_vm_addr` for SDMAv4+.

Generic DQM calls these callbacks after aperture initialization and before hardware programming. QPD fields are later used by `program_sh_mem_settings`, MQD managers, or MES queue input. The file has no independent lifecycle or durable state beyond QPD mutation.

Dependencies include `gc_11_0_0` register masks, `soc21_enum`, `mqd_manager_init_v11`, and `kfd_flat_memory.c` aperture values. It is selected for GC 11.x. Risks are hidden GFX11-specific retry/prefetch/aperture differences not reflected in this simple callback. Test compute and SDMA queues on each GFX11 IP variant, SH_MEM register dumps, flat LDS/scratch workloads, MES scheduling, and cache-policy ioctl behavior.
