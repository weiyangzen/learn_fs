# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.h

Purpose: Declares the quotad service-management interface for glusterd.

Important APIs and types: Includes `glusterd-svc-mgmt.h` for `glusterd_svc_t` and declares `glusterd_quotadsvc_build()`, `glusterd_quotadsvc_init()`, `glusterd_quotadsvc_start()`, `glusterd_quotadsvc_manager()`, and `glusterd_quotadsvc_reconfigure()`.

Control flow: No executable flow is present. The declarations define the callback set installed into `glusterd_svc_t` and called from quota and service-management paths.

State and persistence: State is owned by the `glusterd_svc_t` instance in glusterd private config and by generated quotad volfiles; this header only exposes operations over that state.

Dependencies and integration points: Used by `glusterd-quota.c` and glusterd initialization/service code to manage quotad lifecycle when quota settings change.

Risks: The manager API accepts opaque `void *data` and flags, so callers must pass a `glusterd_volinfo_t *` or `NULL` consistently with implementation expectations.

Test signals: Build linkage, quotad init/build during glusterd startup, quota enable/disable lifecycle, and reconfigure calls after volfile-affecting changes.
