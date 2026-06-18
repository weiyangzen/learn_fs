# subset-b-007102 Research

Grouped source research for GlusterD geo-replication management and gfproxyd service management sources. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.c

## Purpose

`glusterd-geo-rep.c` implements GlusterD's management side of geo-replication. It accepts CLI/RPC requests for system execution, file copy, and `volume geo-replication` operations; validates cluster, volume, secondary, configuration, and state preconditions; drives `gsyncd`, `gverify.sh`, and geo-rep hooks; persists secondary session metadata in `glusterd_volinfo_t`; and builds status responses from gsyncd config/status files. The file was reviewed as a complete 6643-line source.

## Important APIs, Types, and Functions

Public entry points include `glusterd_handle_sys_exec`, `glusterd_handle_copy_file`, `glusterd_handle_gsync_set`, staging functions `glusterd_op_stage_sys_exec`, `glusterd_op_stage_copy_file`, `glusterd_op_stage_gsync_create`, `glusterd_op_stage_gsync_set`, execution functions `glusterd_op_sys_exec`, `glusterd_op_copy_file`, `glusterd_op_gsync_create`, `glusterd_op_gsync_set`, and status helpers `gsync_status`, `glusterd_check_geo_rep_configured`, `_get_secondary_status`, `glusterd_check_geo_rep_running`, and `glusterd_get_gsync_status_mst`.

Important internal helpers include URL normalization/canonicalization (`glusterd_urltransform*`, `parse_secondary_url`, `glusterd_get_secondary_info`, `glusterd_get_secondary_details_confpath`), secondary persistence (`glusterd_store_secondary_in_info`, `glusterd_remove_secondary_in_info`, `glusterd_update_secondary_voluuid_secondaryinfo`), config/status fetchers (`glusterd_gsync_get_config`, `glusterd_gsync_get_status`, `glusterd_get_statefile_name`, `glusterd_fetch_values_from_config`, `glusterd_read_status_file`), lifecycle helpers (`glusterd_check_gsync_running_local`, `glusterd_op_verify_gsync_start_options`, `glusterd_op_verify_gsync_running`, `stop_gsync`, `gd_pause_or_resume_gsync`, `glusterd_gsync_delete`), create helpers (`glusterd_verify_secondary`, `glusterd_create_essential_dir_files`, `create_conf_file`), and config mutation (`gsync_verify_config_options`, `glusterd_gsync_configure`, `glusterd_gsync_op_already_set`).

File-local data includes `gsync_confopt_vals`, which constrains values for selected config options, `gsync_reserved_opts`, which prevents users from changing core gsyncd-managed settings, `gsync_no_restart_opts`, which marks config keys that do not require session restart, and `struct secondary_vol_config`, used to track secondary host/user/index/volume UUID matches.

## Control Flow

RPC handlers decode `gf_cli_req` dictionaries, attach the local `host-uuid`, choose `GD_OP_GSYNC_CREATE` for create requests or `GD_OP_GSYNC_SET` for other geo-rep operations, and enter the GlusterD synchronized op state machine under the big lock. Staging validates op-version support, volume existence, secondary URL shape, canonicalized secondary host/volume data, generated config path, statefile availability, peer liveness, FUSE availability for start, `gsyncd` spawnability, and operation-specific conditions such as an inactive session for delete or a running session for pause/resume/stop.

Create staging additionally verifies the secondary with `gverify.sh` unless `no_verify` is set, handles force bypass rules, validates common PEM and hook-script prerequisites for `push-pem`, gets the remote secondary volume UUID, detects existing sessions by UUID, and records `old_secondaryhost`/`existing_session` when force-create should reuse a previous session directory. Create execution prepares hook arguments, optionally renames an existing session directory, creates the geo-rep working/log directories, creates `gsyncd.conf` with repeated `--config-set-rx` commands, creates an initial `Created` status file, stores the normalized secondary entry in `volinfo->gsync_secondaries`, and enables marker/changelog volume options before regenerating volfiles and managing services.

Start execution records the secondary in `volinfo->gsync_active_secondaries`, upgrades old secondary records with volume UUIDs if needed, then delegates process launch to `glusterd_start_gsync()` in `glusterd-utils.c`, which sets `session-owner` and runs `gsyncd --monitor` for local brick paths. Stop sends `SIGTERM` and then `SIGKILL` to the gsyncd process group found from the pid file, updates the status file to `Stopped`, and removes the active-secondary marker. Pause/resume send `SIGSTOP`/`SIGCONT` to the process group and update the status file to `Paused` or `Started`, with rollback/error messaging when status-file updates fail. Config operations invoke `gsyncd --config-*`, short-circuit if the requested value is already present, create replacement status files for `state_file`, and restart the session unless the key is in `gsync_no_restart_opts`. Delete removes secondary metadata, asks `gsyncd --delete` to clean session state, and removes the session working directory.

Status flow can target all volumes, one volume, or one volume/secondary pair. It resolves stored secondaries to normalized secondary URLs and config paths, fetches `state_file`, working directory, and socket values from gsyncd config, reads monitor status, then gathers per-local-brick `gf_gsync_status_t` data via `gsyncd --status-get` and returns those structs in the response dictionary as `status_valueN` entries plus `gsync-count`.

## State and Persistence Behavior

Persistent cluster/session state is split between GlusterD volume metadata and files under the GlusterD workdir/logdir. `volinfo->gsync_secondaries` stores `secondaryN` values in the format `<primary host uuid>:ssh://{user@}<secondary host>::<secondary volume>:<secondary volume uuid>` and is persisted by `glusterd_store_volinfo(..., GLUSTERD_VOLINFO_VER_AC_INCREMENT)`. Runtime state uses `volinfo->gsync_active_secondaries`, which is updated on start, stop, pause, resume, and restart.

Geo-rep files live under paths like `$workdir/geo-replication/<primary>_<secondary_host>_<secondary_vol>/gsyncd.conf`, `monitor.pid`, `monitor.status`, detail status files, sockets, and session working directories. Logs live under `$logdir/geo-replication/...` and `$logdir/geo-replication-secondaries/...`. `create_conf_file()` writes the gsyncd config by issuing many `gsyncd --config-set-rx` commands for remote gsyncd paths, SSH commands, pid/status/socket paths, log paths, changelog mode, delete behavior, and secondary-side settings. Status files are created/rewritten through `gsyncd --create <status>`.

The code intentionally unlocks `priv->big_lock` around potentially blocking external commands (`gsyncd`, `gverify.sh`, peer helper commands) and relocks afterward. It also uses pid-file lock state to infer whether gsyncd is running.

## Dependencies and Integration Points

Direct internal dependencies include GlusterD op state machine, store, utility, volgen, service helper, message logging, dictionaries, UUID helpers, volume/brick lists, peer liveness checks, hook handling, and volume option storage. External integration is heavy: `GSYNCD_PREFIX/gsyncd`, `GSYNCD_PREFIX/gverify.sh`, `peer_*` helper commands, SSH key files under `geo-replication`, create hooks under `hooks/1/gsync-create/post`, FUSE availability, pid-file locking, Unix signals, and filesystem operations under the GlusterD workdir.

The file participates in `GD_OP_GSYNC_CREATE`, `GD_OP_GSYNC_SET`, `GD_OP_SYS_EXEC`, and `GD_OP_COPY_FILE`. It is also coupled to `glusterd_start_gsync()` in `glusterd-utils.c`, `glusterd_hooks` for create hooks, snapshot code through `gsync_active_secondaries`, and volume set/volgen behavior through marker and changelog knobs.

## Risks and Edge Cases

This file has a large security and correctness surface because it constructs external command arguments, copies files, parses URLs, sends signals to process groups, and mutates persistent cluster state. Notable safeguards include runner argument APIs instead of shell strings, rejecting sys-exec command names containing `/`, realpath containment checks for copy-file source paths, reserved-option validation for gsync config, statefile/template fallback checks, op-version gates, peer-up gates, and force-specific bypasses. Remaining risks include subtle URL parsing mistakes around users/hosts with delimiters, off-by-one termination in copied host/user strings, stale pid files or lock state causing wrong running/not-running decisions, partial persistence when config/status creation succeeds but volume-info storage or marker/changelog updates fail, and inconsistencies when pause/resume signal delivery and status-file updates diverge.

Several operations rely on status/config files generated by `gsyncd`; corrupted or missing config triggers template fallback in some paths but hard failure in others. Force create/stop deliberately bypasses some checks, which is operationally useful but increases the chance of stale metadata, renamed working directories, or secondary identity conflicts if used incorrectly.

## Test Signals

Useful coverage includes CLI integration tests for create/start/stop/pause/resume/config/status/delete with and without `force`; URL normalization tests for root and non-root secondaries; duplicate secondary detection by canonical URL and secondary volume UUID; config validation tests for reserved keys, hyphen/underscore aliases, allowed enum/boolean values, and no-restart keys; fault-injection tests for missing `gsyncd`, missing `gverify.sh`, missing PEM/hook scripts, corrupt config, missing statefile, stale pidfile, down peers, no local bricks, and unavailable `/dev/fuse`; and persistence tests verifying `gsync_secondaries`, `gsync_active_secondaries`, session directories, status files, and marker/changelog volume options after success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.h

## Purpose

`glusterd-geo-rep.h` is the public GlusterD header for geo-replication management helpers implemented by `glusterd-geo-rep.c`. It centralizes path and size constants, exposes config-option value metadata, defines small status callback parameter structs, and declares the status/configured/running checks used by other GlusterD modules. The file was reviewed as a complete 65-line header.

## Important APIs, Types, and Functions

Key macros are `GSYNC_CONF_TEMPLATE`, `GLUSTERD_COMMON_PEM_PUB_FILE`, `GLUSTERD_CREATE_HOOK_SCRIPT`, `SECONDARY_URL_INFO_MAX`, and `VOLINFO_SECONDARY_URL_MAX`. `GSYNC_CONF_TEMPLATE` points to the default gsyncd template under `GEOREP`; the PEM and hook constants define the common public key and create-post hook required for push-pem flows; the URL-size macros bound formatted secondary strings and persisted secondary records.

`struct gsync_config_opt_vals_` describes a geo-rep config option, allowed values, value count, and case sensitivity. `glusterd_gsync_status_temp_t` carries a response dict, volume, and node name through secondary-status iteration. `gsync_status_param_t` carries a volume and an active-session flag through checks that block unsafe volume operations.

Declared functions include `gsync_status`, `glusterd_check_geo_rep_configured`, `_get_secondary_status`, `glusterd_check_geo_rep_running`, and `glusterd_get_gsync_status_mst`.

## Control Flow

The header has no runtime control flow. It is included by GlusterD code that needs to ask whether geo-replication is configured or active, retrieve status into a response dictionary, or call lower-level pid-file status checks.

## State and Persistence Behavior

No storage is owned by the header. Its constants describe persistent files under the GlusterD workdir, and its structs pass pointers to existing dictionaries and `glusterd_volinfo_t` objects. The state semantics are implemented in `glusterd-geo-rep.c`.

## Dependencies and Integration Points

The header depends on GlusterD types such as `dict_t`, `data_t`, `glusterd_volinfo_t`, `gf_boolean_t`, and UUID/login/path sizing macros supplied by surrounding GlusterFS headers. It is the compile-time bridge between geo-replication implementation code and other GlusterD modules that need to prevent volume actions while geo-rep sessions are configured or running.

## Risks and Edge Cases

The URL-size macros must remain aligned with the persisted secondary format. If the persisted format changes without updating `VOLINFO_SECONDARY_URL_MAX`, callers may silently truncate or reject valid secondaries. Exposing `_get_secondary_status` despite its underscore naming also means external callers could depend on an iterator callback shape that is really implementation-specific.

## Test Signals

Compile coverage should catch missing type dependencies and declaration drift. Behavioral tests should indirectly cover this header through volume operations blocked by active geo-rep sessions, status retrieval by volume and by secondary, default-template fallback, and push-pem create flows that require the PEM and hook paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-geo-rep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.c

## Purpose

`glusterd-gfproxyd-svc-helper.c` provides helper routines for GlusterD's per-volume `gfproxyd` service. It builds service paths, checks whether the gfproxy feature is enabled, compares generated gfproxyd volfiles with stored volfiles, and maps a generic `glusterd_svc_t` back to the owning `glusterd_volinfo_t`. The file was reviewed as a complete 234-line source.

## Important APIs, Types, and Functions

Path builders include `glusterd_svc_build_gfproxyd_rundir`, `glusterd_svc_build_gfproxyd_socket_filepath`, `glusterd_svc_build_gfproxyd_pidfile`, `glusterd_svc_build_gfproxyd_volfile_path`, `glusterd_svc_build_gfproxyd_logdir`, and `glusterd_svc_build_gfproxyd_logfile`. State/config helpers include `glusterd_is_gfproxyd_enabled`, `glusterd_svc_check_gfproxyd_volfile_identical`, `glusterd_svc_check_gfproxyd_topology_identical`, and `glusterd_gfproxyd_volinfo_from_svc`.

The file-local `glusterd_svc_get_gfproxyd_volfile` constructs the canonical volfile path, creates a secure temporary file with `mkstemp`, asks `glusterd_build_gfproxyd_volfile()` to generate current expected content, and returns both paths to comparison callers.

## Control Flow

Service code calls the path builders during gfproxyd initialization and process startup. Reconfigure code calls the comparison helpers: they generate a temporary candidate volfile, compare it with the persisted volfile byte-for-byte or topology-only, unlink the temporary file, and report whether the service can be reconfigured in place or needs a restart. `glusterd_gfproxyd_volinfo_from_svc()` uses `cds_list_entry` twice to recover the embedded `glusterd_gfproxydsvc_t` and then its containing `glusterd_volinfo_t`.

## State and Persistence Behavior

The helpers do not persist service state themselves. They derive paths from `THIS->private`, `volinfo`, and `MY_UUID`; generated temporary volfiles live under `/tmp/g<svc_name>-XXXXXX` and are unlinked after comparison or on generation failure. Persistent paths include the volume pid directory for rundir/socket/pid files, the volume directory for `<volname>.gfproxyd.vol`, and the configured GlusterD logdir under `gfproxy/<volname>/gfproxyd.log`.

## Dependencies and Integration Points

The file depends on GlusterD utility macros such as `GLUSTERD_GET_VOLUME_PID_DIR`, `GLUSTERD_GET_VOLUME_DIR`, socket path shortening via `glusterd_set_socket_filepath`, volfile generation via `glusterd_build_gfproxyd_volfile`, comparison helpers `glusterd_check_files_identical` and `glusterd_check_topology_identical`, and volume option lookup with `VKEY_CONFIG_GFPROXY`. It is consumed directly by `glusterd-gfproxyd-svc.c`.

## Risks and Edge Cases

Path truncation is partly handled for socket path construction but less explicit in simple `snprintf` path builders. Temporary volfile handling is careful about unlinking on failure, but callers depend on `tmpvol` ownership and cleanup being followed exactly. The container-of conversion assumes the passed `glusterd_svc_t` is embedded in a `glusterd_gfproxydsvc_t`; passing a different service type would produce invalid ownership rather than a safe type check.

## Test Signals

Useful tests include path construction with long volume names and UUIDs, gfproxy option enable/disable parsing, temporary volfile cleanup on generation failure, byte-identical versus topology-identical reconfigure decisions, and service-to-volume recovery through an initialized `volinfo->gfproxyd.svc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.h

## Purpose

`glusterd-gfproxyd-svc-helper.h` declares the helper surface for the GlusterD gfproxyd service implementation. It exposes path builders, volfile comparison helpers, the gfproxy enabled check, and the generic-service-to-volume conversion used by the service manager. The file was reviewed as a complete 51-line header.

## Important APIs, Types, and Functions

The declarations are `glusterd_svc_build_gfproxyd_rundir`, `glusterd_svc_build_gfproxyd_socket_filepath`, `glusterd_svc_build_gfproxyd_pidfile`, `glusterd_svc_build_gfproxyd_volfile_path`, `glusterd_svc_build_gfproxyd_logdir`, `glusterd_svc_build_gfproxyd_logfile`, `glusterd_svc_check_gfproxyd_volfile_identical`, `glusterd_svc_check_gfproxyd_topology_identical`, `glusterd_is_gfproxyd_enabled`, and `glusterd_gfproxyd_volinfo_from_svc`.

## Control Flow

The header has no executable flow. Its callers use the path builders during service initialization, the comparison helpers during reconfiguration, and `glusterd_is_gfproxyd_enabled()` in manager decisions.

## State and Persistence Behavior

No state is owned here. The declared functions operate on caller-provided buffers, `glusterd_volinfo_t`, and `glusterd_svc_t`. The implementation derives file paths for pid, socket, volfile, and log artifacts but persistence belongs to the service and volfile layers.

## Dependencies and Integration Points

The header includes `glusterd.h` for service and volume types. It is included by both the gfproxyd service implementation and any other GlusterD code that needs to compare gfproxyd volfiles or derive gfproxyd runtime paths.

## Risks and Edge Cases

All path-builder APIs take raw character buffers and lengths; callers must pass buffers large enough for GlusterD path conventions. The header does not annotate ownership for comparison helper outputs because allocation is implementation-local, so misuse is mostly prevented by the narrow function signatures.

## Test Signals

Compile tests should catch declaration drift between the helper header and implementation. Runtime coverage should come through gfproxyd init, start, reconfigure, and restart tests that exercise every declared helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.c

## Purpose

`glusterd-gfproxyd-svc.c` implements the GlusterD service lifecycle for the per-volume `gfproxyd` process. It wires the service vtable, initializes connection/process metadata, creates gfproxyd volfiles, starts and stops `glusterfsd` as gfproxyd, restarts gfproxyd for all started volumes, and decides whether reconfiguration can be handled in place or requires a manager restart. The file was reviewed as a complete 450-line source.

## Important APIs, Types, and Functions

Public functions are `glusterd_gfproxydsvc_build`, `glusterd_gfproxydsvc_stop`, `glusterd_gfproxydsvc_init`, `glusterd_gfproxydsvc_manager`, `glusterd_gfproxydsvc_start`, `glusterd_gfproxydsvc_restart`, and `glusterd_gfproxydsvc_reconfigure`. The file-local `glusterd_gfproxydsvc_create_volfile` wraps `glusterd_generate_gfproxyd_volfile()` with logging.

`glusterd_gfproxydsvc_build()` assigns the service's manager/start/stop/reconfigure callbacks. `glusterd_gfproxydsvc_init()` populates `svc->name`, creates the rundir and logdir, initializes RPC connection state on the gfproxyd Unix socket, and initializes process metadata with pidfile, logfile, volfile, volfile ID, and volfile server. `glusterd_gfproxydsvc_start()` assembles the `glusterfsd` command line.

## Control Flow

Manager flow first initializes the service if needed. It reads `VKEY_CONFIG_GFPROXY` through `glusterd_is_gfproxyd_enabled()`. If gfproxy is enabled but the volume is not started, it stops any running gfproxyd. If gfproxy is enabled and the volume is started, it regenerates the volfile, stops any current gfproxyd, starts a new process, references the volume, and connects the service RPC connection. If gfproxy is disabled while the process is running, it stops the service.

Start flow ensures the volfile exists, optionally wraps the command in Valgrind according to daemon command-line settings, builds a gfproxyd brick id, runs `SBIN_DIR/glusterfsd` with `-s <volfileserver>`, `--volfile-id gfproxyd/<volname>`, pid/log paths, `--brick-name`, `-S <socket>`, optional memory accounting and localtime logging, and assigned brick-port/listen-port xlator options. It uses `pmap_assign_port()` to allocate or reuse `volinfo->gfproxyd.port` and supports both no-wait and synchronous execution, releasing `priv->big_lock` around synchronous process execution.

Reconfigure flow checks whether the service is initialized, enabled, and running. It compares current and generated volfiles byte-for-byte; if identical, nothing happens. If only options changed and topology is identical, it regenerates the volfile and calls `glusterd_fetchspec_notify(THIS)` so the running process fetches updated specs. If topology changed or prerequisites are not met, it delegates to the manager for a stop/start path. Restart flow iterates all started volumes in `conf->volumes` and calls each gfproxyd manager with `PROC_START_NO_WAIT`.

## State and Persistence Behavior

The service state is embedded in `volinfo->gfproxyd.svc`; the port is stored in `volinfo->gfproxyd.port` and reset to zero on stop. Runtime artifacts are pid files, sockets, volfiles, and logs derived by the helper file. The generated volfile is persisted under the volume directory as `<volname>.gfproxyd.vol`. The code does not write volume metadata directly, but it relies on volinfo status/options and updates in-memory process/connection state.

## Dependencies and Integration Points

The implementation depends on generic GlusterD service helpers (`glusterd_svc_stop`, `glusterd_svc_create_rundir`, `glusterd_conn_init`, `glusterd_conn_connect`, `glusterd_proc_init`, `glusterd_proc_is_running`), volfile generation (`glusterd_generate_gfproxyd_volfile`), volfile comparison helpers from `glusterd-gfproxyd-svc-helper.c`, port-map assignment, event reporting through `gf_event(EVENT_SVC_MANAGER_FAILED, ...)`, and `glusterfsd` process startup. It integrates with volume lifecycle by inspecting `glusterd_is_volume_started(volinfo)` and with daemon options such as bind address, Valgrind tool, memory accounting, and localtime logging.

## Risks and Edge Cases

The manager intentionally stops before every enabled-volume start, so startup failures can leave gfproxyd down after a previously running instance was stopped. A failed `glusterd_conn_connect()` unreferences the volume and reports service-manager failure, but the process may already have been started. Port assignment must remain consistent with the generated volfile and `--xlator-option <volname>-server.listen-port`. Long names can stress volfile IDs, brick names, log paths, and socket paths. Reconfigure correctness depends on topology comparison accurately distinguishing restart-required graph changes from live-updateable option changes.

## Test Signals

Useful tests include manager behavior for enabled/disabled gfproxy across started/stopped volumes, missing-volfile creation on start, no-wait versus synchronous start paths, port reuse/reset on restart/stop, localtime and memory-accounting argument inclusion, Valgrind argument construction, byte-identical and topology-identical reconfigure paths, fetchspec notification for option-only changes, and failure cases for logdir creation, process init, process start, and connection failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.h

## Purpose

`glusterd-gfproxyd-svc.h` defines the GlusterD gfproxyd service type and declares its lifecycle functions. It is the public contract used by volume/service code to embed, build, manage, start, stop, reconfigure, and restart gfproxyd. The file was reviewed as a complete 43-line header.

## Important APIs, Types, and Functions

The header defines `gfproxyd_svc_name` as `"gfproxyd"` and `struct glusterd_gfproxydsvc_`, which embeds `glusterd_svc_t svc`, a `gf_store_handle_t *handle`, and an integer `port`. It typedefs this as `glusterd_gfproxydsvc_t`.

Declared lifecycle functions are `glusterd_gfproxydsvc_build`, `glusterd_gfproxydsvc_manager`, `glusterd_gfproxydsvc_start`, `glusterd_gfproxydsvc_stop`, `glusterd_gfproxydsvc_reconfigure`, and `glusterd_gfproxydsvc_restart`.

## Control Flow

The header has no runtime flow. Callers embed `glusterd_gfproxydsvc_t` in `glusterd_volinfo_t`, call `glusterd_gfproxydsvc_build()` to populate the generic service callbacks, then drive lifecycle through the generic `glusterd_svc_t` manager/start/stop/reconfigure pointers or the declared concrete functions.

## State and Persistence Behavior

The only state described here is the service wrapper: generic process/connection state in `svc`, an optional store handle, and the assigned gfproxyd port. Persistence details for pid files, sockets, volfiles, and logs are implemented in the `.c` and helper files.

## Dependencies and Integration Points

The header includes `glusterd-svc-mgmt.h`, so it depends on the generic GlusterD service-management abstraction. It is included by gfproxyd implementation code and by volume structures that need the concrete `glusterd_gfproxydsvc_t` layout.

## Risks and Edge Cases

Because `glusterd_gfproxydsvc_t` embeds `glusterd_svc_t`, helper code uses container-of style conversions. Any layout change must preserve that embedding relationship or update `glusterd_gfproxyd_volinfo_from_svc()`. The `handle` member is declared here but not exercised by the reviewed service code, so future persistence use should clarify ownership and lifetime.

## Test Signals

Compile coverage should catch service signature drift. Runtime coverage should verify that `glusterd_gfproxydsvc_build()` installs the expected function pointers and that a `glusterd_volinfo_t` containing this struct can be initialized, started, stopped, reconfigured, and restarted through the generic service-management path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-gfproxyd-svc.h -->
