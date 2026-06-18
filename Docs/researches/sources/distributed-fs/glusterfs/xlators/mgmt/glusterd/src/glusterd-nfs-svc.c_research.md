# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.c

## Purpose

`glusterd-nfs-svc.c` wires the legacy Gluster NFS service into GlusterD's generic service-management framework. It is compiled only when `BUILD_GNFS` is defined. The file decides whether the NFS service should run, generates the NFS volfile, starts/stops the service, deregisters portmap entries when stopping, and reconfigures or restarts NFS when volume topology/options change.

## Important APIs and functions

`glusterd_nfssvc_build()` is the public builder that installs service callbacks into a `glusterd_svc_t`: manager, start, and stop. `glusterd_nfssvc_reconfigure()` is the public reconfiguration entry point. Internal helpers include `glusterd_nfssvc_need_start()`, which scans all volumes and returns true when at least one started volume has NFS enabled; `glusterd_nfssvc_create_volfile()`, which builds the service volfile path and calls `glusterd_create_global_volfile(build_nfs_graph, ...)`; `glusterd_nfssvc_manager()`, which initializes/stops/regenerates/starts/connects the service as needed; `glusterd_nfssvc_start()`, a thin wrapper over `glusterd_svc_start()`; and `glusterd_nfssvc_stop()`, which calls `glusterd_svc_stop()` and deregisters NFS pmap if the process had been running.

## Control flow

The manager lazily initializes the service with name `nfs`, kills any existing instance, treats missing `XLATORDIR "/nfs/server.so"` as a soft nonfatal condition, writes a fresh global NFS volfile, and starts/connects the service only if `glusterd_nfssvc_need_start()` finds an eligible started volume. Reconfiguration first validates private config and checks for the NFS xlator. It exits successfully if no volume is started. It then compares the generated NFS volfile with the active one by content. If identical, it does nothing. If only topology is identical but options differ, it rewrites the volfile and sends `glusterd_fetchspec_notify()` so the service can reconfigure. If topology differs, it calls the service manager with `PROC_START_NO_WAIT` to restart NFS.

## State and persistence behavior

The file mutates `glusterd_svc_t` callback fields and `svc->inited`, starts/stops `svc->proc`, connects `svc->conn`, and writes the generated NFS service volfile under the GlusterD workdir. It reads each `glusterd_volinfo_t` status and volume dictionary option `NFS_DISABLE_MAP_KEY`; the default value of `1` means volumes are treated as NFS-disabled unless the option is explicitly false. Stopping an active service deregisters NFS from pmap to avoid stale port mappings.

## Dependencies and integration points

The code depends on generic service management (`glusterd-svc-mgmt`, `glusterd-svc-helper`), volfile generation (`glusterd-volgen`, `build_nfs_graph`), process and connection helpers, event emission (`gf_event(EVENT_SVC_MANAGER_FAILED, ...)`), Gluster syscall wrappers, and the install path for the NFS server xlator. It is integrated from the GlusterD service initialization path through `glusterd_nfssvc_build()`.

## Risks and edge cases

Because the manager stops the existing service before checking whether `nfs/server.so` is installed or writing the new volfile, missing xlator or volfile-generation failure can leave NFS stopped. This is probably deliberate for clean reconfiguration but is operationally visible. `glusterd_nfssvc_need_start()` starts the service if any started volume has NFS enabled, so option defaults and volume dictionaries must be correct. Reconfigure relies on volfile equivalence and topology comparison helpers; false positives can skip needed restarts, while false negatives can restart unnecessarily.

## Test signals

Tests should cover build-time exclusion without `BUILD_GNFS`, manager initialization, missing xlator soft success/failure behavior, no eligible volumes, one started NFS-enabled volume, stop pmap deregistration only when process was running, identical volfile no-op, options-only reconfigure through fetchspec notify, topology-change restart, and failure event emission when manager operations fail.
