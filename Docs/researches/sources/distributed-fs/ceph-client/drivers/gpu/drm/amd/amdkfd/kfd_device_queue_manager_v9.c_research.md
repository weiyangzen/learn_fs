# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c

This file provides GFX9 DQM ASIC callbacks, including SDMAv4 simplification and per-process retry/XNACK SH_MEM updates.

`device_queue_manager_init_v9` installs GFX9 cache policy, QPD update, SDMA VM initialization, and MQD manager callbacks. `compute_sh_mem_bases_64bit` encodes independent LDS and scratch high bits. `set_cache_memory_policy_v9` initializes unaligned SH_MEM config, optional global retry disable from `noretry`, F8 mode for GC 9.4.3/9.4.4, high-precision MFMA mode for GC 9.5.0 when requested, disabled APE1, and computed bases. `update_qpd_v9` lazily initializes SH_MEM config and toggles retry disable for per-process XNACK. `init_sdma_vm_v9` clears SDMA VM address.

The generic DQM invokes update during process registration and cache-policy setup. QPD state must match process XNACK and GC-version feature bits. The state is later programmed through SH_MEM settings or MES queue input.

Dependencies include Vega/GFX9 masks, `mqd_manager_init_v9`, process flags, `KFD_SUPPORT_XNACK_PER_PROCESS`, and device `noretry`. Risks are retry-disable inversion, stale SH_MEM config after XNACK changes, and GC 9.4/9.5 feature-bit regressions. Test XNACK on/off, GC 9.4 F8 workloads, GC 9.5 high-precision MFMA flag, SDMA queues, and retry/no-retry VM fault behavior.
