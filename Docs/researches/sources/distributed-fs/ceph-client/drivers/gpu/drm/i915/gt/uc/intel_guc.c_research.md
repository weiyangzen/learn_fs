# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.c

### Purpose
`intel_guc.c` is the central GuC lifecycle and communication implementation. It initializes GuC submodules, configures firmware parameters, manages interrupts, sends MMIO/CT messages, handles early crash notifications, allocates GuC-addressable memory, authenticates HuC, and sanitizes/suspends GuC state.

### Important APIs, Types, And Functions
Important exports include `intel_guc_init_early()`, `intel_guc_init_late()`, `intel_guc_init_send_regs()`, `intel_guc_write_params()`, `intel_guc_init()`, `intel_guc_fini()`, `intel_guc_notify()`, `intel_guc_send_mmio()`, `intel_guc_to_host_process_recv_msg()`, `intel_guc_crash_process_msg()`, `intel_guc_auth_huc()`, `intel_guc_suspend()`, `intel_guc_resume()`, `intel_guc_allocate_vma()`, `intel_guc_allocate_and_map_vma()`, `intel_guc_self_cfg32()`, `intel_guc_self_cfg64()`, `intel_guc_load_status()`, `intel_guc_write_barrier()`, and `intel_guc_dump_time_info()`.

### Control Flow
Early init sets firmware/log/CT/submission/SLPC/RC structures, work items, locks, interrupt hooks, scratch-register base/count, notify register, and early message mask. Full init creates firmware, log, capture, ADS, CT, optional submission and SLPC structures, builds params, and marks firmware loadable. MMIO send serializes on `send_mutex`, writes request dwords into scratch regs, posts, notifies GuC, waits for GuC-origin HXG response, handles busy/retry/failure/success, and optionally copies response dwords. Suspend sends client soft reset when submission is used, then sanitizes CT and interrupts. Allocation creates lmem or shmem GEM objects, pins above the GuC WOPCM bias and below `GUC_GGTT_TOP`, and optionally maps them.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `struct intel_guc`: firmware, log, CT, SLPC, capture, ADS, submission state, interrupt hooks, send registers, params, message masks, timestamp worker, TLB lookup, and dead-GuC worker. Dependencies include GT uncore/interrupts/runtime PM, GuC ABI headers, GEM/VMA allocation, ADS/capture/submission/SLPC modules, and firmware core. Integration spans HuC auth, GuC submission, GT power management, CTB setup, debugfs status, reset/error handling, and GSC write barriers. Risks include protocol timeouts, incorrect busy/retry handling, forcewake domains, reserved GGTT ranges, repeated dead-GuC wedging, suspend cleanup with outstanding G2H, and platform workaround flags. Test signals include GuC boot status, scratch-register dumps, CT readiness, crash notification behavior, self-config KLV acceptance, and memory offset assertions.
