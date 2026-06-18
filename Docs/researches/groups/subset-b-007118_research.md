# Research: subset-b-007118

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-ops.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-ops.c

## Purpose

`glusterd-volume-ops.c` implements the glusterd management-plane handlers, stage checks, and commit-side actions for core volume lifecycle and operational commands. It covers CLI/RPC request handling for create, start, stop, delete, heal, statedump, and clear-locks, then supplies the corresponding op-state-machine callbacks that validate distributed preconditions and mutate `glusterd_volinfo_t` state. The file sits between the CLI wire format (`gf_cli_req`/`gf_cli_rsp` dictionaries), the glusterd transaction engines (`glusterd_op_begin_synctask()` and `glusterd_mgmt_v3_initiate_all_phases()`), persistent volume storage, brick process control, volfile generation, and auxiliary services such as snapd, shd, quotad, gfproxyd, and NFS-Ganesha.

## Important APIs, Types, And Functions

The public handlers are `glusterd_handle_create_volume()`, `glusterd_handle_cli_start_volume()`, `glusterd_handle_cli_stop_volume()`, `glusterd_handle_cli_delete_volume()`, `glusterd_handle_cli_heal_volume()`, and `glusterd_handle_cli_statedump_volume()`. Each wraps an internal `__glusterd_handle_*` implementation with `glusterd_big_locked_handler()`, so CLI decoding and operation launch run under the global glusterd lock.

The stage callbacks are `glusterd_op_stage_create_volume()`, `glusterd_op_stage_start_volume()`, `glusterd_op_stage_stop_volume()`, `glusterd_op_stage_delete_volume()`, `glusterd_op_stage_heal_volume()`, `glusterd_op_stage_statedump_volume()`, and `glusterd_op_stage_clearlocks_volume()`. They are the distributed validation layer: check volume existence and IDs, quorum, brick ordering, brick paths, brick xattrs, geo-rep/NFS/rebalance blockers, self-heal daemon compatibility, quota/statedump constraints, snapshot delete blockers, and peer liveness.

The commit callbacks are `glusterd_op_create_volume()`, `glusterd_op_start_volume()`, `glusterd_op_stop_volume()`, `glusterd_op_delete_volume()`, `glusterd_op_heal_volume()`, `glusterd_op_statedump_volume()`, and `glusterd_op_clearlocks_volume()`. Helpers include `glusterd_start_volume()`, `glusterd_stop_volume()`, `glusterd_client_statedump()`, `glusterd_client_statedump_submit_req()` through the daemon file, and clear-locks helpers that mount a maintenance client and send an xattr command.

Key data passed through the file is `dict_t` operation metadata, `glusterd_conf_t` daemon state, `glusterd_volinfo_t` persistent volume state, `glusterd_brickinfo_t` brick membership, `glusterd_svc_t` service managers, `gf_cli_req`/`gf_cli_rsp` RPC payloads, `gf_xl_afr_op_t` heal operations, and `gf_boolean_t` flags. It also relies heavily on UUIDs (`volume-id`, `MY_UUID`, `GF_XATTR_VOL_ID_KEY`) to keep distributed operations tied to the intended volume.

## Control Flow

Request handlers decode XDR CLI requests with `xdr_to_generic()`, unserialize the embedded dictionary, fetch mandatory keys, add derived fields when needed, and then launch a transaction. Create-volume enriches the request with `transport.address-family`, a generated `volume-id`, and generated internal auth username/password before `glusterd_op_begin_synctask(GD_OP_CREATE_VOLUME, dict)`. Start-volume uses the mgmt-v3 transaction path. Stop-volume uses mgmt-v3 for clusters at op-version `GD_OP_VERSION_4_1_0` and newer, otherwise falls back to the older synctask framework. Delete, heal, and statedump use the synctask framework in this file.

The create stage first rejects duplicate volumes, parses the requested brick list and volume type, validates brick order for replicate/disperse volumes unless `force` is set, creates temporary `glusterd_brickinfo_t` objects, resolves hostnames to UUIDs, checks local brick path length and validity, creates/validates local brick directories, discovers local mount directories, and writes per-brick mount-dir values into the response dictionary for the commit phase. The commit creates a new `glusterd_volinfo_t`, fills type, counts, transport, UUID, auth secrets, replica/disperse/thin-arbiter metadata, brick IDs, local `statvfs` fsid, default options, address-family, and operation-version metadata. It persists the result with `glusterd_store_volinfo()`, creates volfiles and notifies services, then links the volume into `priv->volumes`.

Start validation checks quorum and volume ID, rejects already-started volumes without `force`, validates local brick directories and `GF_XATTR_VOL_ID_KEY`, optionally repairs the xattr under `force`, and returns missing mount-dir data. Commit updates local brick mount-dir state from the transaction dictionary, disables gluster-nfs when the global NFS-Ganesha flag is enabled, starts all bricks through `glusterd_start_volume()`, persists started status, then starts or refreshes snapd, gfproxyd, and other services.

Stop validation verifies volume ID, started state, geo-rep is not active, Ganesha export state is handled, and no rebalance is in progress unless the caller used force for the early state check. Commit stops each brick, marks the volume stopped, persists the new volinfo version, and refreshes snapd and service graphs. Delete validation requires a stopped volume, no snapshots, and all peers up, then marks `volinfo->stage_deleted`; commit disables Ganesha export when needed and calls `glusterd_delete_volume()`.

Heal has two paths. Heal enable/disable and granular-entry-heal enable/disable are translated into a `GD_OP_SET_VOLUME` transaction by setting `key1`, `value1`, and `count` in the request. Other heal commands add brick host/path entries to the dictionary and stage-check volume start state, self-heal daemon enablement, replicate/disperse compatibility, and shd online state before brick-side heal handling. Statedump dispatches to quotad, NFS, client callback statedump, or per-brick statedump. Clear-locks validates volume/path/kind/type, starts a temporary trusted-client mount with self-heal disabled and local brick port xlator options, issues a `GF_XATTR_CLRLK_CMD` getxattr on the target path, returns `lk-summary`, and then unmounts/removes the temporary mount.

## State And Persistence Behavior

The file is a primary writer of volume lifecycle persistence. `glusterd_op_create_volume()` stores a new volinfo and rolls back store state on failure. `glusterd_start_volume()` and `glusterd_stop_volume()` persist status with `GLUSTERD_VOLINFO_VER_AC_INCREMENT` when status changes; start protects the store update with `volinfo->lock` because attach-brick callbacks can update the same record. Create and start propagate local brick `mount_dir` values from stage response dictionaries into durable brickinfo fields. Create also records internal authentication material, volume UUID, replica/disperse counts, thin-arbiter brick metadata, default options, and calculated operation-version bounds.

Side effects include brick directory creation/validation, local brick xattr reads/writes, process starts/stops for bricks and services, volfile generation, service graph notifications, Ganesha export edits, temporary maintenance client mounts under `/tmp`, and state queries through pmap. Many functions intentionally continue best-effort for multi-brick operations, such as statedump, but lifecycle operations generally abort on the first failed brick unless `force` semantics explicitly allow continuing.

## Dependencies And Integration Points

The file depends on glusterd core headers, op-sm and mgmt-v3 transaction machinery, store helpers, brick utilities, volume generation, snapshot utilities, service managers, shd/snapd/gfproxyd support, server quorum, geo-rep checks, NFS-Ganesha helpers, quotad/NFS statedump functions, pmap, runner helpers, dict serialization, RPC/XDR types, and Gluster common/syscall wrappers. Its output dictionaries and callback names are consumed by the glusterd op-state-machine and mgmt-v3 framework. Its persistent updates are later restored by `glusterd_restore()` during daemon initialization and consumed by volfile generation in `glusterd-volgen`.

## Risks

This code has high operational blast radius. Dictionary key mismatches between handler, stage, and commit phases can cause distributed transaction failures or partially populated state. Force handling is intentionally asymmetric and can create or repair volume-id xattrs, so regressions can either reject valid recovery flows or mask unsafe brick reuse. Create-volume parses brick strings with `strtok_r()` and assumes CLI-provided counts match token content, making count/list validation important. Lifecycle persistence must remain ordered with volfile generation and service notification; failures after storing volinfo but before volfile/service completion can leave recovery work for subsequent daemon starts. Clear-locks temporarily releases `big_lock` while running mount/umount commands, so cleanup and lock reacquisition paths are important. Delete staging depends on all peers being up and `stage_deleted` state to avoid races with peer import or snapshot state. Several paths allocate `op_errstr` strings and dynamic dict strings; ownership conventions must be preserved to avoid leaks or double frees.

## Test Signals

Useful tests are Gluster CLI lifecycle tests for create/start/stop/delete across distribute, replicate, disperse, arbiter, and thin-arbiter layouts; bad brick order and `force` create cases; start with missing brick dirs and wrong/missing `trusted.glusterfs.volume-id` xattrs; server-quorum and peer-down rejection; geo-rep, rebalance, snapshot, and Ganesha blockers; heal enable/disable and shd offline cases; quotad/NFS/client/brick statedump dispatch; and clear-locks integration that verifies maintenance mount cleanup and `lk-summary` reporting. Regression tests should also exercise old op-version stop fallback versus mgmt-v3 stop, and restart persistence by creating or changing a volume, restarting glusterd, and checking restored volinfo, volfiles, brick status, and services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-set.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-set.c

## Purpose

`glusterd-volume-set.c` is the central option map and glusterd-side validation layer for `gluster volume set`, `volume reset`, and volfile option generation. It defines `glusterd_volopt_map[]`, a large `struct volopt_map_entry` dispatch table that maps user-facing volume/global option keys to translator types, translator option names, defaults, documentation visibility, operation-version gates, flags, descriptions, and optional validation callbacks. The file contains no top-level CLI handler; instead, other volume-set and volgen code uses this table to decide which keys are accepted, how they are documented, how values are validated, and how options are applied into client, brick, NFS, management, and feature translator graphs.

## Important APIs, Types, And Functions

The exported data is `glusterd_volopt_map[]`. Each entry has fields such as `.key`, `.voltype`, `.option`, `.value`, `.type`, `.flags`, `.op_version`, `.description`, and `.validate_fn`. Plain options map directly to xlator options on matching graph nodes. Special options have an `.option` beginning with `!` and are interpreted by glusterd/volgen-specific logic rather than copied mechanically into every translator of that type.

Validation callbacks include `validate_cache_max_min_size()`, `validate_defrag_throttle_option()`, `validate_quota()`, `validate_uss()`, `validate_uss_dir()`, `validate_server_options()`, `validate_disperse()`, `validate_replica()`, `validate_quorum_count()`, `validate_subvols_per_directory()`, `validate_replica_heal_enable_disable()`, `validate_mandatory_locking()`, `validate_disperse_heal_enable_disable()`, `validate_lock_migration_option()`, `validate_mux_limit()`, `validate_volume_per_thread_limit()`, `validate_boolean()`, `validate_disperse_quorum_count()`, `validate_parallel_readdir()`, `validate_rda_cache_limit()`, `validate_worm_period()`, `validate_reten_mode()`, and `validate_statedump_path()`. These functions receive `glusterd_volinfo_t *volinfo`, the request dictionary, key/value strings, and `char **op_errstr`, then return zero or failure with a user-facing error.

## Control Flow

Validation functions are called by the volume-set operation path before the new value is stored into the volume dictionary or global options. Most callbacks parse the proposed value, inspect the current `volinfo`, and set `*op_errstr` on failure. Examples include cache min/max cross-validation against the existing opposite value; quota options requiring quota to be enabled; USS directory names requiring a dot prefix, bounded length, and limited characters; server integer options rejecting negative or non-integer values; quorum count bounded by replica count; disperse quorum bounded by data count and disperse count; and statedump path requiring an existing directory.

The option table is consumed later by volgen. Entries identify the translator family (`cluster/distribute`, `cluster/replicate`, `cluster/disperse`, `protocol/client`, `protocol/server`, `performance/*`, `features/*`, `storage/posix`, `mgmt/glusterd`, `nfs/server`, and others), whether the option is client-visible via `VOLOPT_FLAG_CLIENT_OPT`, whether it enables/disables a translator via `VOLOPT_FLAG_XLATOR_OPT`, whether reset should skip it with `VOLOPT_FLAG_NEVER_RESET`, and whether internal force behavior is needed with `VOLOPT_FLAG_FORCE`.

The table is arranged by subsystem: DHT/distribute options, NUFA/switch special cases, AFR/replicate and disperse heal/locking/quorum options, diagnostics/io-stats, performance translators, protocol client/server and socket/TLS options, perf translator enable/disable switches, features such as snapshots/USS/quota/marker/bitrot/trash/locks/shard/upcall/leases/cloudsync/ctime/simple-quota, NFS options when `BUILD_GNFS` is enabled, storage/posix options, and management/global options such as quorum, op-version, shared storage, brick multiplexing, daemon logging, and thread tuning.

## State And Persistence Behavior

The file itself does not write persistent state. It defines the metadata that determines which values may be persisted into `volinfo->dict` or glusterd's global option dictionary by the surrounding volume-set operation code. Defaults in `.value` can affect generated volfiles even when a key is absent from the volume dictionary. `.op_version` protects mixed-version clusters by preventing use of options before all peers understand them. `.type` controls whether an option is public documentation (`DOC`/`GLOBAL_DOC`) or internal/no-doc (`NO_DOC`/`GLOBAL_NO_DOC`), which affects CLI help and stability expectations.

Some validators inspect current persistent state: `glusterd_volinfo_get()` reads existing cache-size pairs; `glusterd_volinfo_get_boolean()` checks quota; `glusterd_is_defrag_on()` blocks parallel-readdir changes during rebalance; `glusterd_check_client_op_version_support()` prevents setting large readdir-ahead cache limits when older clients are connected; brick multiplexing validators inspect global brick-mux enablement. These checks make the table both a schema and a policy gate for cluster-safe option mutation.

## Dependencies And Integration Points

This file depends on `glusterd.h`, `glusterd-volgen.h`, and `glusterd-utils.h`, plus common syscall/stat and string conversion helpers. It integrates tightly with the volume-set op implementation, reset/help generation, option validation from translator `xlator_options`, and volfile generation. It also exposes management-plane constants from other headers, including `VKEY_*`, `GLUSTERD_*`, `NFS_DISABLE_MAP_KEY`, TLS option macros, and op-version constants. Many entries are coupled to translator implementation names and option names, so changes in translators must be mirrored here.

## Risks

The largest risk is schema drift: a `.key`, `.voltype`, or `.option` typo can silently prevent an option from reaching the intended translator or can expose an invalid CLI key. Special `!` options are not mechanically applied, so adding one requires understanding the corresponding volgen special-case code. Incorrect `.op_version` values can break rolling upgrades by allowing unknown options, or unnecessarily block valid options. Missing `VOLOPT_FLAG_CLIENT_OPT` can leave client graphs stale while brick graphs change; incorrectly adding it can send server-only options to clients. Validators must set `op_errstr` consistently and preserve ownership conventions. Validators that parse numeric, boolean, bytesize, or path values must match translator expectations, otherwise glusterd can accept a value that later fails during graph generation or translator init.

## Test Signals

Good signals include CLI tests for `volume set help`, accepted/rejected values, reset behavior, and generated volfiles for each major option family. Specific validation tests should cover cache min/max ordering, quota-only options when quota is disabled, USS directory validation, server integer options, replica/disperse-only options on wrong volume types, quorum ranges, lock migration on non-distribute volumes, mandatory-locking enum values, brick multiplexing disabled/enabled limits, volume-per-thread bounds, parallel-readdir while rebalance is active, large readdir-ahead cache with old clients, WORM period parsing, retention mode enums, and statedump path existence. Upgrade tests should verify op-version gating for recently added options such as simple-quota, io_uring, anonymous inode, brick graceful cleanup, and newer DHT/disperse options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volume-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd.c

## Purpose

`glusterd.c` is the management daemon translator entry point. It defines glusterd's RPC program registration, callback transport tracking, daemon initialization, persistent state restoration, working/log/run directory setup, geo-replication bootstrap, mountbroker setup, service construction, option schema, and xlator API hooks. This file is responsible for turning the glusterd xlator into a running management service with TCP and Unix-domain listeners, restored cluster/volume metadata, auxiliary service managers, hooks, and event-thread configuration.

## Important APIs, Types, And Functions

Global program arrays `gd_inet_programs[]` and `gd_uds_programs[]` define which RPC programs are exposed on network listeners and the CLI Unix socket. `gd_op_list[]` maps `glusterd_op_t` values to display strings. The callback program `glusterd_cbk_prog` is used to notify connected clients for fetchspec, fetchsnap, and statedump callbacks.

Initialization helpers include `glusterd_opinfo_init()`, `glusterd_uuid_init()`, `glusterd_uuid_generate_save()`, `glusterd_options_init()`, `glusterd_rpcsvc_options_build()`, `glusterd_program_register()`, `glusterd_init_uds_listener()`, `glusterd_stop_uds_listener()`, `glusterd_stop_listener()`, `glusterd_find_correct_var_run_dir()`, `glusterd_init_var_run_dirs()`, `is_upgrade()`, `is_downgrade()`, and `glusterd_handle_upgrade_downgrade()`.

RPC and callback helpers are `glusterd_client_statedump_submit_req()`, `glusterd_fetchspec_notify()`, `glusterd_fetchsnap_notify()`, and `glusterd_rpcsvc_notify()`. Geo-replication helpers under `SYNCDAEMON_COMPILE` include `glusterd_check_gsync_present()`, `group_write_allow()`, `glusterd_crt_georep_folders()`, `runinit_gsyncd_setrx()`, `run_gsyncd_cmd()`, and `configure_syncdaemon()`. Mountbroker helpers include `check_prepare_mountbroker_root()` and `_install_mount_spec()`.

The xlator lifecycle is provided by `init()`, `fini()`, `notify()`, `mem_acct_init()`, the `options[]` schema, and `xlator_api`.

## Control Flow

`init()` starts by raising file descriptor limits, resolving run/log/work directories from translator options or defaults, creating those directories, setting `GLUSTERD_WORKDIR` and `DEFAULT_VAR_RUN_DIRECTORY`, resolving `/var/run` versus `/run`, creating snap/bitd/scrub/NFS/quotad runtime directories, initializing command history logging, and creating persistent subdirectories such as `vols`, `snaps`, `peers`, `bricks`, service directories, and `groups`.

It then builds RPC options, starts the primary RPC service, registers connection notifications, applies management-plane TLS when `secure_mgmt` is enabled, counts configured transports, creates listeners, and registers all network RPC programs. It starts a separate Unix-domain listener for CLI and getspec traffic through `glusterd_init_uds_listener()`. After listeners are ready, it allocates and initializes `glusterd_conf_t`, list heads, mutexes, synclocks, condition variables, transport tracking, service pointers, port ranges, lock timeouts, valgrind settings, ping timeout, mgmt-v3 locks, and transaction dictionaries.

Service setup builds NFS (when compiled), quotad, bitd, and scrub service objects; creates hooks directories; installs mountbroker specs from options; validates mountbroker root if configured; handles upgrade/downgrade flags; configures syncdaemon when not in upgrade/downgrade mode; restores op-version before service initialization can accidentally generate/store a UUID with a default op-version; restores all stored glusterd state with `glusterd_restore()`; applies localtime logging; handles upgrade/downgrade volfile recreation and self-termination; checks max op-version storage and regenerates volfiles if needed; launches daemon spawning when this is a single-peer node; starts the hooks worker; and finally applies the `event-threads` option to the event pool.

`fini()` stops the UDS and TCP listeners and frees hostname lists. Deeper cleanup is disabled with `#if 0` because running threads may still hold resources. `notify()` mostly forwards unhandled translator events to `default_notify()`.

## State And Persistence Behavior

Persistent identity is managed by `glusterd_uuid_init()` and `glusterd_uuid_generate_save()`, which retrieve or generate the daemon UUID and store it through `glusterd_store_global_info()`. Global options are initialized with `glusterd_options_init()`, restored through `glusterd_store_retrieve_options()`, and written with `glusterd_store_options()` when needed. `init()` restores op-version with `glusterd_restore_op_version()`, restores volumes/peers/snapshots and other durable state with `glusterd_restore()`, stores max op-version with `glusterd_store_max_op_version()`, and can regenerate volfiles when max op-version changes or upgrade metadata is absent.

Runtime state lives in `glusterd_conf_t`: peer, volume, snapshot, missed-snapshot, brick process, shd process, hostname, remote hostname, mount spec, and active transport lists; RPC service handles; work/run/log directories; base/max ports; lock timeout; worker count; service objects; locks and condition variables. Callback transports are added and removed in `glusterd_rpcsvc_notify()` under `xprt_lock`; disconnect also removes pmap entries.

Geo-rep setup creates work and log directories, adjusts group write permissions when a configured log group exists, and writes multiple gsyncd configuration defaults via runner calls. Mountbroker setup validates root ownership and permissions, creates the `MB_HIVE` directory with strict mode, and installs mount specs from translator options into `conf->mount_specs`.

## Dependencies And Integration Points

The file depends on Gluster RPC service infrastructure, dict/options parsing, syscall wrappers, list utilities, syncops, runner commands, pmap, glusterd store/restore, hooks, locks, service managers, geo-rep, mountbroker, statedump, server quorum-related options, and translator registration APIs. It integrates with external programs such as `gsyncd`, `glusterfs`, and system mountbroker filesystem layout. Its RPC program registration exposes peer, CLI, management v3, service management, pmap, handshake, and getspec interfaces. Its callback transport list is used by fetchspec/fetchsnap/statedump notification paths, including volume operations in `glusterd-volume-ops.c`.

## Risks

Initialization order is critical. Op-version restoration must happen before service initialization that may use `MY_UUID`; changing this can corrupt stored op-version defaults. Listeners are created before `glusterd_conf_t` is assigned to `this->private`, so error paths must free partially initialized RPC objects carefully. Directory path lengths and permissions are heavily checked; weakening those checks can break runtime paths or create security exposure around mountbroker and geo-rep log directories. The `fini()` path intentionally avoids full cleanup, so tests should not assume all memory/resources are released before process exit. Geo-rep configuration uses many external runner commands; failures are normalized to `-1` but some directory setup failures are treated as non-fatal depending on path. Transport list updates must remain locked because callback broadcasts iterate over the same list.

## Test Signals

Strong tests include daemon startup with default and custom work/run/log directories; UDS and TCP listener creation; secure management TLS option propagation; registration of all network and UDS programs; restore from existing peer/volume/global-option stores; first-start UUID generation and persistence; op-version restore before service startup; max-op-version mismatch volfile regeneration; upgrade/downgrade flag handling and termination; mountbroker root permission rejection and valid spec installation; geo-rep present/missing behavior; callback notifications to connected clients; event-thread reconfiguration; and shutdown of listeners/sockets in `fini()`. Failure-injection around directory creation, RPC listener creation, dict option parsing, and store restore should verify that init returns failure or exits only in the intended fatal cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd.c -->
