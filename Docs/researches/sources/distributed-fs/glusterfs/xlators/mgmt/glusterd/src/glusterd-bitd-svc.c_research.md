# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.c

Purpose: manages the BitD daemon service used by Gluster bitrot signing. It builds the service object, initializes it, creates the service volfile, starts/stops the process, connects RPC, and decides between live reconfigure and restart.

Important APIs/types/functions: `glusterd_bitdsvc_build()` installs service callbacks. `glusterd_bitdsvc_init()` calls `glusterd_svc_init()` with `bitd`. `glusterd_bitdsvc_create_volfile()` writes the global BitD volfile via `glusterd_create_global_volfile(build_bitd_graph, ...)`. `glusterd_bitdsvc_manager()` initializes and either stops BitD when no local started bitrot volume needs it, or recreates volfile, kills old process, starts it, and connects `svc->conn`. `glusterd_bitdsvc_reconfigure()` compares volfiles/topology and either notifies existing daemons or delegates to the manager.

Control flow: service manager lazily initializes `svc`; `glusterd_should_i_stop_bitd()` gates stop-vs-start. Reconfigure first avoids work when the rendered volfile is identical, then checks topology identity. If only options changed it writes a fresh volfile and sends `glusterd_fetchspec_notify()`. If topology changed, it restarts through the manager.

State and persistence behavior: BitD service state is held in `glusterd_svc_t` (`inited`, callbacks, connection). Persistent/observable artifacts include the generated BitD volfile under glusterd workdir and the running bitd process. No volume options are modified here.

Dependencies and integration points: depends on bitrot policy from `glusterd-bitrot.c`, service helpers, volfile generation (`build_bitd_graph`), generic service start/stop, connection management, and event emission.

Risks and edge cases: killing with `SIGKILL` before start is blunt and can disrupt in-flight work. Incorrect topology identity detection can notify when a restart is needed or restart unnecessarily. RPC connect failure after process start leaves partial service state and emits `EVENT_SVC_MANAGER_FAILED`.

Test signals: enable/disable bitrot across local/nonlocal bricks, reconfigure option-only vs topology-changing cases, no-op identical volfile path, service start/stop failures, and RPC connection establishment.
