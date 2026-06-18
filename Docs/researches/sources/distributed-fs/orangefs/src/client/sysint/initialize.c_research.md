# sources/distributed-fs/orangefs/src/client/sysint/initialize.c
## sources/distributed-fs/orangefs/src/client/sysint/initialize.c

**Purpose:** Implements `PVFS_sys_initialize()`, the staged bring-up for the OrangeFS client sysint runtime.

**APIs and control flow:** Initialization is guarded by a recursive mutex, `pvfs_sys_init_flag`, and `pvfs_sys_init_in_progress`. It sets client PID, gossip debug mask/file from env, parses `PVFS2_RELATIME_TIMEOUT`, initializes events, id generator, distributions, security, encoder, BMI, flow, request scheduler, job time manager, job system, client SM context, acache, capcache, ncache, server config manager, cached config, and posts a job timer state machine retained in global `g_smcb`. A bitmask tracks which subsystems were initialized so `error_exit` can unwind in reverse.

**State and dependencies:** Owns global runtime flags, `g_smcb`, `PINT_client_sys_event_id`, `pint_client_pid`, and `relatime_timeout`. Depends on nearly every sysint subsystem.

**Risks and tests:** On non-Windows, `pvfs_sys_init_in_progress` is never reset on `local_exit` due to `#ifdef WIN32`; success uses the outer flag, but failed init paths can leave confusing state. `pvfs_sys_init_flag` is set to 1 at `local_exit` even when `ret` is negative after some error paths. Tests should simulate subsystem failures, repeated concurrent initialization, env parsing, timer post failure, and full init/finalize cycles.
