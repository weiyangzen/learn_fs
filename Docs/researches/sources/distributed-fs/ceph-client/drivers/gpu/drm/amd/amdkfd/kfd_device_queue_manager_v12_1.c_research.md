# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c

This file provides GFX12.1 DQM ASIC callbacks. It differs from GFX12.0 by programming VM context retry controls and using a different private-base encoding.

`device_queue_manager_init_v12_1` installs `update_qpd_v12_1`, `init_sdma_vm_v12_1`, and `mqd_manager_init_v12_1`; no cache-policy callback is installed. `compute_sh_mem_bases_64bit` uses `lds_base >> 48` for shared base and `scratch_base >> 58` shifted into private base. `update_qpd_v12_1` copies GFXHUB `vm_cntx_cntl`, initializes SH_MEM config with unaligned mode, prefetch, and F8 mode, and toggles both SH_MEM `RETRY_DISABLE` and VM context retry-permission based on per-process XNACK. `init_sdma_vm_v12_1` clears `sdma_vm_addr`.

The generic DQM selects this for GC 12.1+. Process registration updates QPD state, and queue creation/MES input later consumes `sh_mem_config`, `sh_mem_bases`, and `vm_cntx_cntl`. Persistent behavior is per process device and follows `process->xnack_enabled`.

Dependencies include GFX12.1 masks, GFXHUB VM context defaults, `mqd_manager_init_v12_1`, and KFD XNACK support checks. Risks are missing cache-policy behavior, private-base bit encoding mistakes, and desynchronizing SH_MEM retry-disable from VM context retry permission. Test XNACK on/off, retry VM faults, MES queue submission, F8-mode workloads, flat LDS/scratch access, and SDMA queues.
