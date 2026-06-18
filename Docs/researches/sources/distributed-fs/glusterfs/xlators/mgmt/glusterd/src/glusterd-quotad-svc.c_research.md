# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.c

Purpose: Implements the glusterd service wrapper for the quotad daemon. It builds, initializes, starts, stops, restarts, and reconfigures the service based on quota-enabled volume state and generated quotad volfiles.

Important APIs and functions: `glusterd_quotadsvc_build()` installs manager/start/stop callbacks into a `glusterd_svc_t`. `glusterd_quotadsvc_init()` initializes the generic service as `quotad`. `glusterd_quotadsvc_manager()` decides whether to stop or restart quotad. `glusterd_quotadsvc_start()` builds command-line dictionary arguments and calls `glusterd_svc_start()`. `glusterd_quotadsvc_reconfigure()` compares old/new volfiles and either sends a fetchspec notify or restarts via the manager.

Control flow: The manager lazily initializes the service, then stops quotad when all volumes are stopped or all quota-enabled volumes are stopped. Otherwise, if the triggering volume is relevant to quota, it creates the quotad volfile, stops any existing daemon, starts it with the requested flags, and connects the service RPC. Reconfigure first exits to manager if all quota volumes are stopped, then checks whether generated volfiles are byte-identical, topology-identical, or topology-changed to choose no-op, notify, or restart.

State and persistence: Service state lives in `glusterd_svc_t` fields such as `inited`, `name`, callbacks, and connection. Generated quotad volfiles are persisted under the glusterd workdir via `glusterd_svc_build_volfile_path()` and `glusterd_create_global_volfile()`.

Dependencies and integration points: Depends on generic service management (`glusterd-svc-mgmt`, `glusterd-svc-helper`), volfile generation (`build_quotad_graph`), Gluster run/dict helpers, quota volume predicates, fetchspec notify, connection management, and event reporting. `glusterd-quota.c` calls the quotad manager after enable/disable operations.

Risks: Incorrect quota-volume predicates can stop quotad while still needed or keep it running unnecessarily. Reconfigure correctness depends on volfile identity/topology comparison; a false topology match could notify when a restart is required. Startup uses dynamically built command-line dict keys with fixed small key buffers, so argument count assumptions matter.

Test signals: Enabling first quota volume starts quotad, disabling last quota volume stops it, volume option changes trigger fetchspec notify when topology is unchanged, topology changes restart quotad, and service-manager failures emit `EVENT_SVC_MANAGER_FAILED`.
