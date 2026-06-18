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
