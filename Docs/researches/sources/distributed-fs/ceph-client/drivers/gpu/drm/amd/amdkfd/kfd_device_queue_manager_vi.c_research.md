# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c

This file supplies VI/GFX8 DQM ASIC callbacks. It mirrors CIK but uses GFX8 register encodings and memory-type values.

`device_queue_manager_init_vi` installs `set_cache_memory_policy_vi`, `update_qpd_vi`, `init_sdma_vm`, and `mqd_manager_init_vi`. `compute_sh_mem_bases_64bit` encodes the top address nybble into shared/private SH_MEM base fields. `set_cache_memory_policy_vi` validates and encodes APE1, handles zero-sized APE1 disable, selects `MTYPE_UC` for coherent and `MTYPE_NC` otherwise, programs unaligned alignment, and computes SH_MEM bases. `update_qpd_vi` is a no-op. `init_sdma_vm` encodes the shared-base nybble into the SDMA virtual-address field.

State lives in QPD SH_MEM fields and queue `sdma_vm_addr`. Generic DQM later programs that state through `program_sh_mem_settings` or MQD/MES paths. There is no independent persistent state in the file.

Dependencies include GFX8 and OSS masks, VI MQD manager support, and `get_sh_mem_bases_nybble_64`. It is selected for Carrizo, Tonga, Fiji, Polaris, and related GFX8 ASICs. Risks are APE1 representation errors, cache coherency memory-type mistakes, and SDMA VM encoding issues. Test cache policy ioctls, invalid APE1 alignment, coherent/non-coherent variants, SDMA queues, and GFX8 flat-memory addressing.
