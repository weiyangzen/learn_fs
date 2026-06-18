# sources/distributed-fs/orangefs/src/client/sysint/finalize.c
## sources/distributed-fs/orangefs/src/client/sysint/finalize.c

**Purpose:** Shuts down the PVFS system interface and releases client-side subsystems initialized by `PVFS_sys_initialize()`.

**APIs and control flow:** `PVFS_sys_finalize()` is guarded by a static mutex and `finiflag`. It finalizes id generation, optionally dumps ncache/acache/capcache counters based on `PVFS2_COUNTERS_AT_FINALIZE`, then tears down capcache, ncache, acache, cached config, server config manager, job timers/context/job layer, flow, scheduler, timer queue, BMI, encoder, security, distributions, events, pvfstab, and gossip. It releases global timer SMCB `g_smcb` and resets the Windows init flag.

**State and dependencies:** Depends on global job context, global `g_smcb`, perf counters, env vars, and every initialized sysint subsystem.

**Risks and tests:** Finalize order is critical because timers and perf counters may reference state-machine context and caches. It calls `job_close_context` directly even though `PINT_client_state_machine_finalize()` also wraps that. `PINT_client_state_machine_release(g_smcb)` must tolerate null/previously completed timer SMCBs. Tests should cover repeated finalize, finalize without successful initialize, counter dump env values, and partial initialization failure cleanup.
