# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c

This file supplies DQM ASIC callbacks for CIK/GFX7 devices. It installs the CIK MQD manager and implements CIK SH_MEM cache policy and SDMA VM aperture setup.

`device_queue_manager_init_cik` fills `device_queue_manager_asic_ops` with `set_cache_memory_policy_cik`, `update_qpd_cik`, `init_sdma_vm`, and `mqd_manager_init_cik`. `compute_sh_mem_bases_64bit` maps the process LDS/scratch/GPUVM top-address nybble into CIK `SH_MEM_BASES`. `set_cache_memory_policy_cik` validates alternate aperture encoding, handles zero-sized APE1 as disabled, programs base/limit, selects default and APE1 memory types, preserves `PTR32`, sets unaligned alignment mode, and computes `sh_mem_bases`. `update_qpd_cik` is a no-op. `init_sdma_vm` encodes the shared-base nybble for SDMA.

The generic DQM invokes these callbacks during process registration, cache policy setup, and SDMA queue creation. Persistent state is in the QPD and queue properties: SH_MEM config, APE1 base/limit, SH_MEM bases, and `sdma_vm_addr`.

Dependencies include GFX7/OSS register masks, `get_sh_mem_bases_nybble_64`, CIK MQD manager support, and generic DQM `program_sh_mem_settings`. It is selected for Kaveri and Hawaii. Risks are APE1 alignment/representability mistakes, user/kernel aperture crossing, and memory-type coherency changes. Test cache policy ioctls, zero-sized APE1 disable, invalid base/limit rejection, SDMA queue creation, and CIK/Hawaii no-HWS queue loading.
