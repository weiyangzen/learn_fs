# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.c

## Purpose
Manages the global bitrot scrub service named `scrub`: service vtable setup, initialization, volfile generation, start/stop decisions, and reconfiguration when the scrub graph changes.

## Important APIs, types, and functions
`glusterd_scrubsvc_build()` installs manager/start/stop hooks on a `glusterd_svc_t`. `glusterd_scrubsvc_init()` calls `glusterd_svc_init()` with `scrub_svc_name`. `glusterd_scrubsvc_manager()` initializes on demand, creates a scrub volfile, kills any old process, restarts the generic service, and reconnects its RPC connection unless bitd policy says it should stop. `glusterd_scrubsvc_stop()` delegates to `glusterd_svc_stop()`. `glusterd_scrubsvc_reconfigure()` compares old/new volfile contents and topology, then either notifies fetchspec or restarts through the manager.

## Control flow
The manager first ensures `svc->inited`, then branches on `glusterd_should_i_stop_bitd()`. Stop policy sends `SIGTERM`; otherwise it regenerates the global volfile with `build_scrub_graph`, stops the process with `SIGKILL`, starts with supplied flags, and calls `glusterd_conn_connect()`. Reconfigure avoids work when the generated volfile is byte-identical, sends a fetchspec notification for option-only changes, and restarts when topology changed or the service should stop.

## State and persistence behavior
Persistent state is the generated scrub volfile under the GlusterD workdir. Runtime state is held in the shared `glusterd_svc_t`: `inited`, process metadata, connection metadata, and service name. Failures emit `EVENT_SVC_MANAGER_FAILED`.

## Dependencies and integration points
Uses `glusterd-svc-mgmt`, generic service helpers, `glusterd-volgen`'s `build_scrub_graph`, bitrot policy helper `glusterd_should_i_stop_bitd()`, fetchspec notification, and Gluster event/logging APIs. It integrates with the broader daemon-service reconfigure path.

## Risks and test signals
Risks include unnecessary `SIGKILL` restarts for option-only changes, stale volfiles after failed generation, missed RPC reconnects after restart, and start/stop behavior when bitrot is disabled mid-reconfigure. Tests should exercise identical volfile no-op, topology-identical fetchspec notification, topology-changed restart, bitd-stop branch, failed volfile creation, and service-manager event emission.
