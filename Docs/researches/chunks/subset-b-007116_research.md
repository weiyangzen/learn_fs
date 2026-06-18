# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.c lines 8648-12989

## Scope

This chunk covers the second half of `glusterd-utils.c`, beginning inside the tail of the rebalance restart helper and continuing through management response aggregation, volume-option/default-option helpers, brick-operation prerequisites, brick-order validation, temporary `auth.allow` expansion, and snapshot filesystem label changes. The code is primarily utility glue for glusterd management operations: it translates node-local state and peer replies into operation dictionaries, checks preconditions before disruptive brick operations, derives volfile paths and option values, and updates selected in-memory and persistent volume state.

## Purpose

The chunk provides support routines used by glusterd's distributed operation paths after CLI requests are accepted and peer/node RPCs start returning data. Several functions fold per-node dictionaries into an originator operation context so CLI responses can show aggregate volume status, rebalance status, profile data, heal data, bitrot/scrub state, and client lists. Other helpers decide whether the local daemon should restart a rebalance worker, validate volume identity, map CLI operation strings to glusterd operation enums, and prepare source/destination brick metadata for reset-brick or replace-brick flows.

The chunk also handles cluster compatibility and persistence-adjacent behavior: it computes volume/client op-version requirements from set options, enables version-dependent defaults on newly created or reset volumes, removes quota store files, temporarily widens `auth.allow` during brick operations, restores and stores the old `auth.allow`, and runs filesystem-specific tools to relabel snapshot backends.

## Important APIs, Types, and Functions

- Rebalance state: `glusterd_restart_rebalance_for_volume()`, `glusterd_volinfo_reset_defrag_stats()`, `glusterd_defrag_volume_status_update()`, `gd_should_i_start_rebalance()`, `glusterd_volume_rebalance_use_rsp_dict()`, `glusterd_rebalance_rsp()`, and `glusterd_defrag_volume_node_rsp()` work with `glusterd_volinfo_t`, `glusterd_rebalance_t`, `gf_defrag_status_t`, and rebalance dictionaries keyed as `files-N`, `status-N`, `time-left-N`, `node-uuid-N`, and related counters.
- Status/profile/heal aggregation: `glusterd_profile_volume_use_rsp_dict()`, `glusterd_volume_status_copy_to_op_ctx_dict()`, `glusterd_heal_volume_brick_rsp()`, `glusterd_status_volume_brick_rsp()`, `glusterd_status_volume_client_list()`, and `glusterd_handle_node_rsp()` convert node-local response dictionaries into originator dictionaries using `glusterd_pr_brick_rsp_conv_t`, `glusterd_status_rsp_conv_t`, and `glusterd_heal_rsp_conv_t`.
- Task and originator handling: `glusterd_set_originator_uuid()`, `is_origin_glusterd()`, `glusterd_generate_and_set_task_id()`, and `glusterd_copy_uuid_to_dict()` store origin/task UUIDs in `dict_t` objects and allow older peers to fall back to the transaction lock owner.
- Option and op-version support: `_update_volume_op_versions()`, `gd_update_volume_op_versions()`, `glusterd_enable_default_options()`, `glusterd_get_value_for_vme_entry()`, `glusterd_get_global_options_for_all_vols()`, `glusterd_get_default_val_for_volopt()`, and `glusterd_get_volopt_content()` depend on `glusterd_volopt_map`, `volopt_map_entry`, translator dynamic option loading, `valid_all_vol_opts`, and `glusterd_conf_t::opts`.
- Brick operation support: `glusterd_handle_replicate_brick_ops()`, `assign_brick_groups()`, `get_last_brick_of_brick_group()`, `glusterd_get_rb_dst_brickinfo()`, `rb_update_dstbrick_port()`, `glusterd_brick_op_prerequisites()`, `glusterd_get_dst_brick_info()`, `glusterd_get_volinfo_from_brick()`, `gd_cli_to_gd_op()`, and `gd_rb_op_to_str()` prepare and validate add/replace/reset brick flows.
- Topology and comparison helpers: `glusterd_check_topology_identical()` builds two graphs from volfiles and calls `is_graph_topology_equal()`, while `glusterd_check_files_identical()` compares file size and `get_checksum_for_path()` output.
- Placement/auth/snapshot helpers: `glusterd_check_brick_order()` compares resolved host addresses within replica/disperse sets; `glusterd_add_peers_to_auth_list()` and `glusterd_replace_old_auth_allow_list()` mutate `volinfo->dict` and regenerate volfiles; `glusterd_update_mntopts()` records backend mount type/options; `glusterd_update_fs_label()` invokes `xfs_admin` or `tune2fs`.

## Control Flow

Rebalance restart begins by asking `gd_should_i_start_rebalance()` whether this node owns a relevant brick. Normal rebalance starts when any local volume brick matches `MY_UUID`; remove-brick migration starts only if one of the bricks listed in `volinfo->rebal.dict` is local. If the node should not start a worker, `glusterd_restart_rebalance_for_volume()` marks status as not started and returns success so status reporting still has task metadata. Otherwise it requires a stored rebalance command and calls `glusterd_volume_defrag_restart()` with a remove-brick callback when applicable. The tail of `glusterd_volume_defrag_restart()` in this chunk reuses or recreates the defrag RPC client depending on defrag object reference count, starts missing workers, and emits `EVENT_REBALANCE_START_FAILED` on failures.

Status aggregation is dictionary driven. `glusterd_handle_node_rsp()` dispatches per-node replies by operation: profile replies are prefixed with a per-brick count, status replies become `brick<index>.<field>` entries or client-list counters, defrag replies update `volinfo->rebal` and emit rebalance keys, heal replies translate self-heal daemon keys from replica/child coordinates to brick indexes, and scrub status adds bitrot/scrubber metadata. `glusterd_volume_status_copy_to_op_ctx_dict()` then merges peer status dictionaries into the originator context, preserving originator volume lists for `status all`, shifting remote brick indexes after `brick-index-max`, updating `count`/`other-count`, and optionally aggregating task state.

Task aggregation has a separate precedence rule. On the first response, `glusterd_volume_status_aggregate_tasks_status()` copies all `task*` keys. Later responses must have the same task count, identify matching tasks by `taskN.id`, skip "Replace brick" tasks because those are reported from local `rb_status`, and rank rebalance task status as `STARTED` over `FAILED` over `STOPPED` over `COMPLETE` over `NOT_STARTED`. This rank is intentionally tied to CLI XML output behavior noted in the source comments.

Option flows are split between retrieval and mutation. `glusterd_get_global_options_for_all_vols()` handles `volume get all`-style global options, including a special all-peer phase for maximum op-version. `glusterd_get_default_val_for_volopt()` walks `glusterd_volopt_map` and checks global options, volume options, local special defaults for replicate volumes, static map values, and translator-provided defaults. `glusterd_get_volopt_content()` builds the help output, either text in `help-str` or XML when libxml support is compiled in. `gd_update_volume_op_versions()` walks the current volume dictionary, raises `op_version` and `client_op_version` for enabled options, adds special handling for automatically enabled open-behind, and forces disperse volumes to at least `GD_OP_VERSION_3_6_0`.

Brick operation flow validates broadly before local action. `glusterd_brick_op_prerequisites()` maps the CLI operation string, finds and verifies the volume is started, rejects active geo-replication or rebalance, requires FUSE availability, resolves the source brick, exports its local port in the response dictionary, and fills the local brick pidfile when the source brick is on this node. `glusterd_get_dst_brick_info()` parses `dst-brick` as host/path, validates stored path and volfile path lengths, duplicates the string before splitting at the final colon, and constructs a `glusterd_brickinfo_t`. `glusterd_handle_replicate_brick_ops()` then marks AFR dirty xattrs on a brick, mounts a temporary client, sets add/replace-brick xattrs on the mounted client, and lazily unmounts.

## State and Persistence Behavior

Most functions mutate in-memory `dict_t` and `glusterd_volinfo_t` state rather than directly writing stable storage. Rebalance status fields in `volinfo->rebal` are updated from response dictionaries, but many fields are only assigned if the reported value is nonzero; `time_left` is the exception because successful retrieval of zero is meaningful. `glusterd_volinfo_reset_defrag_stats()` clears counters but leaves command, operation, task id, and status alone.

Operation contexts are aggregated dictionaries. They are keyed by string conventions shared with CLI code and peer RPC code, so state shape is part of the inter-module contract: `count`, `other-count`, `brick-index-max`, `taskN.*`, `node-uuid-N`, `files-N`, `clientN.name`, and similar keys must stay consistent. `glusterd_to_cli()` also consumes `cmd-str`, logs success/failure through `gf_cmd_log()`, submits the RPC reply, and unreferences the dictionary.

Persistent or durable effects appear in a few focused helpers. `glusterd_clean_up_quota_store()` unlinks the volume quota config and checksum files under the glusterd volume directory, destroys the quota store handle, and resets quota version state. `glusterd_replace_old_auth_allow_list()` restores `auth.allow` from `old.auth.allow`, regenerates volfiles, notifies services, and calls `glusterd_store_volinfo()` with `GLUSTERD_VOLINFO_VER_AC_INCREMENT`. `glusterd_add_peers_to_auth_list()` changes `volinfo->dict` and regenerates volfiles but intentionally keeps `old.auth.allow` for later restoration. `glusterd_update_fs_label()` changes backend filesystem metadata by running external filesystem tools, not by updating glusterd's store directly.

## Dependencies and Integration Points

The chunk depends heavily on GlusterFS core utilities: `dict_t` accessors, `data_copy()`, `gf_uuid_*`, `gf_msg`/`gf_smsg` logging, `gf_event`, `runner_t`, `synctask_new()`, `synclock`, RCU/list macros, store/path macros, and memory helpers such as `GF_MALLOC`, `GF_CALLOC`, `GF_FREE`, and `gf_strdup`. It also uses system APIs including `fopen()`, `stat`, `getaddrinfo()`, `getnameinfo()`, mount table parsing via `struct mntent`, xattrs, and external programs `glusterfs`, `xfs_admin`, and `tune2fs`.

Important glusterd integration points include peer lists and global config in `glusterd_conf_t`, volume and brick metadata in `glusterd_volinfo_t` and `glusterd_brickinfo_t`, service log paths for bitrot/scrub, the management v3 phase engine for `GD_OP_MAX_OPVERSION`, rebalance/defrag RPC creation and callbacks, geo-replication status checks, client transport lists guarded by `xprt_lock`, and volfile generation/notification through `glusterd_create_volfiles_and_notify_services()`.

CLI and RPC integration is implicit in dictionary key contracts. The CLI expects `help-str`, status counts, task status, client process counts, rebalance metrics, scrub details, and global option `keyN`/`valueN` pairs. Node RPC handlers call `glusterd_handle_node_rsp()` with operation enums such as `GD_OP_PROFILE_VOLUME`, `GD_OP_STATUS_VOLUME`, `GD_OP_DEFRAG_BRICK_VOLUME`, `GD_OP_HEAL_VOLUME`, and `GD_OP_SCRUB_STATUS`.

## Risks and Edge Cases

Several helpers treat missing dictionary keys as benign because peer replies vary by node role. This is useful for aggregation, but it can hide malformed responses: profile replies without `count` return success with no bricks, rebalance aggregation logs missing counters and continues, and bitrot fields are added only when present.

`glusterd_defrag_volume_status_update()` only updates most counters when values are nonzero. A legitimate transition from a nonzero counter back to zero would not be reflected, although such counters normally increase. The `status` field also is not updated when the status enum value is zero, which is safe only if zero maps to the intended "not started" default and stale nonzero status should not be overwritten by absent/zero responses.

Dictionary key parsing is string-format sensitive. `_profile_volume_add_friend_rsp()` and `_status_volume_add_brick_rsp()` use `sscanf()`/`snprintf()` conventions; heal aggregation parses replica and child ids from hyphen-delimited keys; status aggregation parses `brick%d.%s`. Any upstream key format change can silently skip or mis-index data.

The task status rank array indexes directly by `remote_status` and `local_status`. It assumes values are within the known `GF_DEFRAG_STATUS_*` range. Unexpected status enum values could read outside the initialized rank table.

`glusterd_get_dst_brick_info()` uses the final colon to split host and path to tolerate IPv6 addresses, but the check `if (!host || !path)` tests the address of the output pointer parameter rather than `!*host`/`!path` content. In practice `path` is initialized from `c`, so malformed strings without a colon still set no `path` and are caught only because `path` remains `NULL`; the `host` half of the condition is weaker than intended.

`search_peer_in_auth_list()` uses substring matching against the comma-separated `auth.allow` value, so a peer name that is a substring of another allowed hostname can be treated as already present. `glusterd_add_peers_to_auth_list()` also assumes `GF_CALLOC()` succeeds before `strncat()`.

`glusterd_check_brick_order()` resolves hostnames and compares numeric addresses, which catches aliases but depends on DNS consistency and allocates an addrinfo list for both new and existing bricks. The second, `flag`-controlled check compares new entries against all existing bricks, but the loop bound uses the count of existing bricks while advancing through the new-brick list, so small new lists with larger existing counts deserve close test coverage.

Temporary mount flows in `glusterd_handle_replicate_brick_ops()` unlock `priv->big_lock` while running the external mount command and relock afterward. That prevents blocking the daemon lock during process execution, but it means callers must tolerate state changes while the command runs. Failure paths before lazy unmount can leave the temporary directory in place; the code unmounts after setting the xattr but does not visibly remove the `mkdtemp()` directory in this chunk.

`glusterd_get_value_for_vme_entry()` and `glusterd_get_volopt_content()` dynamically load translator option tables and close handles on each iteration. Missing translator options are intentionally swallowed in some paths, so help/default output can omit options if a translator cannot be loaded.

## Test Signals

Useful tests for this chunk should exercise dictionary shape and status aggregation rather than only individual return codes:

- Rebalance restart on a mixed cluster where only nodes with relevant bricks start defrag, including remove-brick restart setting `decommission_in_progress`.
- Rebalance status aggregation with peer order changes, op-version below and above `GD_OP_VERSION_6_0`, zero `time-left`, nonzero promoted/demoted counters, and failed/missing peer responses.
- `volume status` for all volumes, single volumes, task-only status, and client-list status, checking `count`, `other-count`, `brick-index-max`, `taskN.status`, `client-count`, and per-process counters.
- Heal status/statistics replies from shd where only local bricks should contribute `-status` or statistics keys after replica/child-to-brick-id translation.
- Bitrot scrub status when options are explicitly set and when defaults are used, including bad-GFID quarantine lists.
- Volume get/help paths with and without libxml support, missing translator modules, global options, max-op-version, per-volume defaults, and replicate-special defaults.
- Brick operation prerequisite failures for stopped volumes, active geo-replication, active rebalance, unavailable FUSE, missing source brick, overlong destination paths, IPv6 destination bricks, and local source/destination port propagation.
- Brick-order validation for replica/disperse sets with aliases resolving to the same address, unresolvable names, incomplete brick strings, add-brick with existing replica sets, and force behavior at higher layers.
- `auth.allow` staging and restoration where peer names overlap as substrings, volfiles are regenerated, `old.auth.allow` is removed, and `glusterd_store_volinfo()` persists the restoration.
- Snapshot backend helpers on xfs, ext2/3/4, unsupported filesystems, missing external tools, and mount-table entries with long filesystem type or mount option strings.

## Cross-Chunk Notes

This chunk relies on earlier parts of `glusterd-utils.c` for volume/brick lookup, defrag setup, volfile path helpers, store macros, op-version map helpers, and many validation utilities. The merge lane should combine this document with `subset-b-007115` to describe the full utility file: the first chunk contains many constructors, store/path helpers, and initial rebalance setup, while this chunk focuses on post-operation aggregation, restart decisions, option/default handling, and brick-operation support.
