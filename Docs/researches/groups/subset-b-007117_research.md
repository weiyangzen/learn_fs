# Research: subset-b-007117

Grouped research for GlusterFS glusterd volume-generation and utility interface files. Each section is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.h

## Purpose

`glusterd-utils.h` is the broad utility contract for the glusterd management daemon. It declares helper types, macros, and APIs used by volume operations, peer synchronization, locking, brick lifecycle management, RPC request handling, snapshot backends, geo-replication, quota, rebalance, mount discovery, and volume option validation. In this work item it is especially relevant because `glusterd-volgen.c` depends on several exported utility APIs for brick iteration state, authentication secrets, local-brick detection, volume state checks, service notification, and volfile path construction.

## Important APIs, types, and functions

- `glusterd_add_dict_args_t`, `glusterd_dict_ctx_t`, and dictionary export/import declarations support serializing glusterd state into RPC dictionaries, peer sync payloads, and CLI responses.
- `glusterd_friend_synctask_args_t` carries peer data, peer version data, and a dynamically sized status array for asynchronous friend synchronization.
- `enum glusterd_vol_comp_status_` names volume comparison outcomes used during peer reconciliation: none, success, update requested, and reject.
- `addrinfo_list_t` and `gf_ai_compare_t` support address resolution and comparison helpers used while validating peer or brick host identities.
- `struct glusterd_lock_` and the lock APIs (`glusterd_get_lock_owner`, `glusterd_lock`, `glusterd_unlock`) expose glusterd's operation lock owner and timestamp state.
- `struct glusterd_snap_ops` is the snapshot backend vtable. LVM and ZFS backends provide probe, details, create, clone, remove, activate, deactivate, restore, and brick-path callbacks.
- Brick and volume lifecycle APIs include `glusterd_volinfo_new`, `glusterd_volinfo_ref`, `glusterd_volinfo_unref`, `glusterd_volinfo_find`, `glusterd_brickinfo_new`, `glusterd_brickinfo_new_from_brick`, `glusterd_brickinfo_delete`, `glusterd_delete_volume`, and `glusterd_delete_brick`.
- Brick runtime APIs include `glusterd_resolve_brick`, `glusterd_volume_stop_glusterfs`, `glusterd_brick_start`, `glusterd_brick_stop`, `send_attach_req`, and status setters/getters such as `glusterd_set_brick_status` and `glusterd_is_brick_started`.
- RPC helper APIs (`glusterd_submit_reply`, `glusterd_to_cli`, `glusterd_submit_request`) centralize XDR and iobuf based request and response submission.
- Volume and peer serialization APIs include `glusterd_add_volume_to_dict`, `glusterd_add_volumes_to_export_dict`, `glusterd_import_volinfo`, `glusterd_import_quota_conf`, and `glusterd_compare_friend_data`.
- Operation aggregation and response merge helpers include `glusterd_sync_use_rsp_dict`, `glusterd_rb_use_rsp_dict`, `glusterd_profile_volume_use_rsp_dict`, `glusterd_volume_status_copy_to_op_ctx_dict`, `glusterd_volume_rebalance_use_rsp_dict`, and `glusterd_handle_node_rsp`.
- Geo-replication helpers include `glusterd_start_gsync`, secondary URL parsing, status-file creation, statefile naming, local-running checks, restart checks, and local brick path collection.
- Quota, bitrot, and service state helpers include `glusterd_is_volume_quota_enabled`, `glusterd_is_bitrot_enabled`, `glusterd_all_volumes_with_quota_stopped`, `glusterd_clean_up_quota_store`, and `glusterd_status_has_tasks`.
- Mount and brick storage helpers include `glusterd_get_brick_mount_device`, `glusterd_get_mnt_entry_info`, `glusterd_get_brick_root`, `glusterd_get_brick_mount_dir`, `glusterd_aggr_brick_mount_dirs`, `glusterd_update_mntopts`, `glusterd_update_fs_label`, and `glusterd_find_brick_mount_path`.
- Volfile and option related declarations used by `glusterd-volgen.c` include `glusterd_get_trusted_client_filepath`, `glusterd_get_dummy_client_filepath`, `glusterd_get_rebalance_volfile`, `glusterd_get_gfproxy_client_volfile`, `glusterd_get_default_val_for_volopt`, `glusterd_get_global_options_for_all_vols`, and `glusterd_check_client_op_version_support`.

## Control flow

This header does not implement runtime control flow, but it defines many control-flow contracts used by glusterd operation code. The management path generally parses CLI or peer RPC dictionaries, resolves `glusterd_volinfo_t` and `glusterd_brickinfo_t` objects through these helpers, validates topology and operation preconditions, starts or stops brick processes, regenerates volfiles, and submits aggregated responses. Several declarations encode two-phase or callback-driven flows: `glusterd_launch_synctask` runs asynchronous work, `send_attach_req` talks to an existing brick multiplex process, `glusterd_handle_node_rsp` merges per-node responses, and `glusterd_snap_ops` dispatches snapshot operations to the configured backend.

For volume generation specifically, `glusterd-volgen.c` calls into utility APIs after it has built graph objects: it uses auth helpers to set protocol credentials, brick-group helpers to determine arbiter placement, path helpers for trusted and dummy client volfiles, local-brick checks for bitrot and scrub graphs, feature status helpers for quota and bitrot service inclusion, and service notification declarations elsewhere in glusterd after volfile writes complete.

## State and persistence behavior

The persistent state surfaced by this header is mostly owned by implementation files. `GLUSTERD_CKSUM_FILE` names the checksum file used for stored volume state. `GLUSTERD_SOCK_DIR` gives the default runtime socket directory. The brick-id macros mutate `glusterd_brickinfo_t` identifiers in a deterministic form (`<volname>-client-<id>` and `<volname>-ta-<id>`), which then appears in generated volfiles and AFR pending xattr option construction. Volume and brick import/export APIs persist and reconstruct state through dictionaries exchanged with peers or loaded from store files. Snapshot APIs persist backend-specific snapshot state through LVM or ZFS operations and restored brick paths. Mount helpers read system mount tables and filesystem labels to attach storage metadata to bricks.

The lock APIs hold glusterd operation ownership in `glusterd_lock_t`. Volume, brick, defrag, and RPC reference helpers expose explicit ref/unref contracts, so callers must treat returned pointers as owned or borrowed according to the implementation contract. Geo-replication helpers create status files and read state files, while quota helpers load and import quota configuration into volume dictionaries.

## Dependencies and integration points

The header includes `glusterd-peer-utils.h` and `glusterfs/compat-uuid.h`, while its declarations rely on core Gluster types such as `xlator_t`, `dict_t`, `rpcsvc_request_t`, `rpc_clnt_t`, `call_frame_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `glusterd_defrag_info_t`, `gf_transport_type`, and many generated RPC/XDR structures. It is a central include for glusterd operation files, including volume ops, brick ops, snapshot code, rebalance code, quota, geo-replication, and volgen.

Important integration points include peer comparison and friend cleanup during cluster membership changes, hook and service layers that react to volume changes, brick multiplexing attach/detach, the store layer that maintains volume metadata, and translator graph generation code that needs stable brick IDs and feature status.

## Risks and edge cases

- The header is very wide and couples unrelated glusterd subsystems. Prototype drift or semantic changes can affect many operation paths.
- `glusterd_friend_synctask_args_t` uses a one-element trailing array pattern for dynamically allocated status values; allocation size mistakes would corrupt adjacent memory.
- `GLUSTERD_ASSIGN_BRICKID_*` macros use `sprintf` into `brick_id`, so safety depends on destination sizing and bounded volume names.
- `ALL_VOLUME_OPTION_CHECK` has control-flow side effects (`goto out` or another label) and allocates error strings. Callers must pass labels and cleanup paths correctly.
- Snapshot backend callbacks are function pointers with many string and brick arguments. A backend that implements only partial validation can break create, clone, restore, or path reconstruction.
- Many APIs return `int` or `int32_t` with mixed conventions across glusterd; callers need to distinguish boolean-like success, errno-like negative values, and Gluster-specific status codes.
- Path and mount helpers operate on system paths, mount entries, and filesystem labels. Tests need to cover long paths, missing mount table entries, bind mounts, and local-vs-remote hostname ambiguity.

## Test signals

Useful signals include compile coverage across files that include `glusterd-utils.h`, unit or functional tests for brick-id assignment, peer volume import/export round trips, operation lock owner transitions, brick start/stop attach paths, mount root detection, geo-rep secondary parsing, quota import and cleanup, and snapshot backend callback behavior. For callers in `glusterd-volgen.c`, key integration tests are volfile regeneration after add/remove/replace-brick, trusted and untrusted client volfile path creation, local-only bitrot/scrub graph inclusion, and shared-brick-count propagation into generated posix translator options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.c

## Purpose

`glusterd-volgen.c` is glusterd's translator graph and volfile generation engine. It converts a `glusterd_volinfo_t`, brick information, cluster topology, and volume option dictionaries into GlusterFS graph objects and writes the resulting `.vol` files for bricks, clients, gfproxyd, snapd, self-heal daemon, quotad, bitrot daemon, scrub daemon, NFS, and rebalance. It also validates volume-set changes by building candidate graphs and running translator option validation against them.

The file is the operational bridge between stored volume metadata and the running translator topology that bricks, clients, and glusterd-managed services consume.

## Important APIs, types, and functions

- Low-level graph helpers: `xlator_instantiate_va`, `volgen_graph_add_as`, `volgen_graph_add_nolink`, `volgen_graph_add`, `volgen_xlator_link`, `volgen_graph_link`, `volgen_graph_merge_sub`, `volgen_graph_free`, and `first_of`.
- Option resolution and validation helpers: `volopt_trie`, `option_complete`, `glusterd_check_option_exists`, `glusterd_check_voloption_flags`, `glusterd_check_globaloption`, `glusterd_check_localoption`, `glusterd_volopt_validate`, `gd_get_vmep`, `glusterd_get_op_version_from_vmep`, `gd_is_client_option`, `gd_is_xlator_option`, and `gd_is_boolean_option`.
- Generic option application: `volgen_graph_set_options_generic` walks `glusterd_volopt_map`, overlays explicit dictionary values on defaults, and invokes handlers such as `basic_option_handler`, `server_spec_option_handler`, `perfxl_option_handler`, `shd_option_handler`, `nfs_option_handler`, `bitrot_option_handler`, and `scrubber_option_handler`.
- Volfile persistence: `volgen_write_volfile` writes to `<target>.tmp`, prints the graph, closes it, renames it into place, and then runs executable filters under `FILTERDIR`; `volgen_apply_filters` performs the filter pass.
- Server graph builders: the `server_graph_table` encodes brick-side translator order through builders such as `brick_graph_add_posix`, `brick_graph_add_changelog`, `brick_graph_add_bitrot_stub`, `brick_graph_add_acl`, `brick_graph_add_locks`, `brick_graph_add_quota`, `brick_graph_add_marker`, `brick_graph_add_index`, `brick_graph_add_io_stats`, `brick_graph_add_upcall`, `brick_graph_add_leases`, and `brick_graph_add_server`.
- Client graph builders: `volgen_graph_build_client`, `volgen_graph_build_clients`, `volgen_graph_build_afr_clusters`, `volgen_graph_build_ec_clusters`, `volgen_graph_build_dht_cluster`, `volume_volgen_graph_build_clusters`, and `client_graph_builder`.
- Service graph builders: `build_rebalance_volfile`, `build_shd_graph`, `build_nfs_graph` when GNFS is enabled, `build_quotad_graph`, `build_bitd_graph`, `build_scrub_graph`, `glusterd_snapdsvc_generate_volfile`, `glusterd_snapdsvc_create_volfile`, `glusterd_build_gfproxyd_volfile`, and `glusterd_generate_gfproxyd_volfile`.
- Final generation entry points: `generate_brick_volfiles`, `generate_client_volfiles`, `generate_dummy_client_volfiles`, `glusterd_generate_client_per_brick_volfile`, `glusterd_create_rb_volfiles`, `glusterd_create_volfiles`, `glusterd_create_volfiles_and_notify_services`, `glusterd_create_global_volfile`, and `glusterd_delete_volfile`.
- Reconfiguration validators: `validate_clientopts`, `validate_brickopts`, `glusterd_validate_brickreconf`, `glusterd_validate_globalopts`, `glusterd_validate_reconfopts`, `validate_shdopts`, and `validate_nfsopts` under GNFS.

## Control flow

The basic graph construction pattern starts with an empty `volgen_graph_t`, adds xlators from the leaf upward, links each new xlator to the previous graph top when appropriate, then applies options from the volume dictionary and optional override dictionary. `build_graph_generic` is the common wrapper: it copies `volinfo->dict`, overlays `mod_dict`, calls a role-specific builder, and then applies generic options.

Brick volfile generation starts in `generate_brick_volfiles`. It checks the marker xtime option, creates or removes the `marker.tstamp` file, assigns brick groups, calculates local shared-brick counts, iterates all bricks, builds a server graph for each brick, and writes each brick volfile. `server_graph_builder` runs `server_graph_table` in reverse so the on-disk posix layer is created first and the protocol/server layer ends up at the graph top. After every named server translator position it can add debug xlators (`debug.trace`, `debug.error-gen`, `debug.delay-gen`) and user xlators (`user/<name>`) according to volume options.

Client volfile generation starts in `generate_client_volfiles`. It enumerates required transports (`tcp`, `rdma`, or both), builds a dictionary with `client-transport-type` and the client trust level, chooses the appropriate volfile path for trusted, gfproxy trusted-proxy, or ordinary clients, and calls `generate_single_transport_client_volfile`. `client_graph_builder` creates protocol/client xlators for each brick, folds them into AFR or EC clusters when needed, adds distribute/NUFA/switch at the top for distributed layouts, then optionally adds cloudsync, shard, utime/ctime, read-only for snapshots, compression, quiesce for gfproxy, quota compatibility, performance translators, snapview-client for user-serviceable snapshots, debug translators, and finally io-stats.

Cluster folding is topology-sensitive. `volgen_graph_build_clients` rejects zero-brick volumes and inconsistent distributed counts, inserts thin-arbiter client xlators at the expected positions, and verifies the actual brick count. `volgen_graph_build_afr_clusters` links replica sets, sets AFR pending-xattr lists, adds volume-id on supported op-version, and configures arbiter or thin-arbiter options. `volgen_graph_build_ec_clusters` links disperse groups and sets redundancy. `volgen_graph_build_dht_cluster` adds distribute, NUFA, or switch and records decommissioned children when a child subtree contains a decommissioned client. `volgen_graph_build_readdir_ahead` can add readdir-ahead below DHT when parallel readdir is enabled.

Service graph flows reuse the same graph primitives with role-specific roots. `build_rebalance_volfile` creates a trusted-client graph only for distributed volumes and writes a rebalance volfile. `build_shd_graph` adds io-stats, builds trusted client subgraphs for replicate or disperse volumes, marks AFR/EC xlators as self-heal daemon consumers, and merges subgraphs into the service graph. `build_quotad_graph` creates a `features/quotad` root and merges one child client graph per started quota-enabled volume. GNFS, when compiled, creates an `nfs/server` root, adds started non-disabled volumes as child graphs, and applies NFS-specific per-volume options. Bitrot and scrub builders iterate started bitrot-enabled volumes, include only local bricks, wrap them in `features/bit-rot`, and set signer or scrubber options.

Reconfiguration validation builds prospective graphs instead of writing them. Brick, client, NFS, and SHD validators attach `graph.errstr` to the caller's error string, build graphs with the candidate dictionary, and call `graph_reconf_validateopt` so translator option validators see the graph they would run with.

## State and persistence behavior

`volgen_write_volfile` is the main persistence primitive. It creates a mode-0600 temporary file, prints the in-memory graph with `glusterfs_graph_print_file`, closes it, atomically renames it to the target path, and then invokes executable volfile filters. A failed write leaves the target unchanged but may leave error logs and a temporary path cleanup responsibility to the filesystem layer.

Path construction mirrors glusterd store layout. Brick volfiles are written under the volume directory using sanitized brick paths and optional prefixes. Client volfiles use trusted, ordinary, gfproxy, dummy, or rebalance path helpers. Snapd, shd, gfproxyd, quotad, bitd, scrub, and NFS volfiles use service-specific path builders outside this file.

`generate_brick_volfiles` creates or removes `marker.tstamp` based on the marker xtime option. For snapshot volumes it copies the parent timestamp to preserve geo-replication semantics. Changelog and index translators store brick-local paths under `.glusterfs/changelogs` and `.glusterfs/indices`. Posix translator options include the brick directory, volume-id, link-count-parent behavior, FIPS checksum mode for newer op-versions, and shared-brick-count. Protocol translators embed authentication usernames, passwords, SSL parameters, address-family, and auth-paths derived from volume state.

In-memory graph state is transient and owned by `volgen_graph_t`; `volgen_graph_free` destroys xlators after writing or validation. Option state comes from `volinfo->dict`, optional override dictionaries, defaults in `glusterd_volopt_map`, and computed mutations such as readdir-ahead cache partitioning, root-squash/open-behind adjustment, trusted-client markings, and service role flags.

## Dependencies and integration points

This file depends on Gluster core graph, dict, list, trie, logging, run-command, option, and xlator APIs. It also integrates tightly with glusterd store, hooks, geo-replication, snapshot utilities, service management helpers, snapd/shd/gfproxyd helpers, and utility APIs from `glusterd-utils.h`.

Key external data and functions include `glusterd_volopt_map` for option mapping, `graph_reconf_validateopt` for translator validation, `glusterd_auth_get_username` and `glusterd_auth_get_password` for protocol credentials, `glusterd_check_geo_rep_configured` for preventing unsafe marker or changelog disables, `assign_brick_groups` and `get_last_brick_of_brick_group` for arbiter placement, `glusterd_is_local_brick` for bitrot/scrub graph scoping, `glusterd_is_volume_quota_enabled` and `glusterd_is_bitrot_enabled` for service inclusion, and `glusterd_fetchspec_notify` for client fetch-spec refresh after volfile regeneration.

The generated volfiles are consumed by brick processes, FUSE/native clients, gfproxyd, snapd, quotad, self-heal daemon, bitrot, scrub, NFS, and rebalance. Many glusterd operation files call `glusterd_create_volfiles_and_notify_services` after volume mutations such as create, set, add-brick, remove-brick, replace-brick, quota changes, bitrot changes, geo-rep changes, rebalance, snapshot operations, and peer synchronization.

## Risks and edge cases

- The translator ordering encoded by `server_graph_table` and client cluster builders is critical. Reordering can change behavior, especially around posix, changelog, bitrot-stub, locks, quota, marker, performance, io-stats, and protocol/server.
- `get_server_xlator` appears to return `GF_XLATOR_SERVER` when `strcmp(xlator, dbg_key)` is nonzero rather than zero, which is suspicious for debug xlator placement validation.
- Several paths depend on `dict_copy` even though comments note it swallows errors. Partial option overlays may produce graphs that validate but do not reflect the intended override set.
- User xlator insertion accepts `user.xlator.<name>` options and builds `user/<name>` translator types. Invalid positions are checked, but translator availability and option semantics depend on runtime xlator loading.
- `volgen_graph_build_clients` must keep thin-arbiter client insertion in lockstep with AFR pending-xattr construction. Off-by-one errors would make AFR child order and pending xattrs disagree.
- Readdir-ahead cache and request sizes are rewritten by dividing across distribute count; invalid byte-size strings or zero values are surfaced through `graph.errstr`.
- Changelog and marker disables are blocked when geo-replication sessions exist. Any bypass in option mapping could disable dependencies that geo-rep expects.
- Multiple functions return early without freeing copied dictionaries in some error branches, so future edits should audit ownership carefully, especially in snapd generation and rebalance dictionary setup.
- `volgen_apply_filters` executes every regular executable in `FILTERDIR` after a volfile write. Filter order depends on directory iteration, and a failed filter is logged but does not roll back the volfile.
- Volfile path construction uses fixed `PATH_MAX` buffers and string formatting. Very long volume names, hostnames, brick paths, or user xlator names should be tested.

## Test signals

High-value tests include generated volfile topology checks for distribute, replicate, disperse, arbiter, thin-arbiter, distributed-replicate, distributed-disperse, and single-brick volumes; option-set validation for client, brick, SHD, NFS, global, and local options; geo-replication protection for changelog and marker disables; root-squash and open-behind interactions; parallel readdir and readdir-ahead size rewriting; shared storage trusted-client filtering; SSL option propagation; gfproxy client/server graphs; snapd and snapview-client graph child ordering; quotad inclusion only for started quota-enabled volumes; bitrot/scrub local-brick selection; marker timestamp creation, deletion, and snapshot timestamp inheritance; and filter execution after atomic volfile writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.h

## Purpose

`glusterd-volgen.h` is the public interface for glusterd's volfile generation engine. It defines canonical volume-option key strings, translator graph roles, option-map metadata, builder callback types, brick and client xlator insertion enums, and the functions used by the rest of glusterd to build, validate, create, and delete volfiles.

This header keeps callers insulated from the implementation details in `glusterd-volgen.c` while exposing enough metadata for volume-set validation, option completion, client-op-version calculation, and service-specific graph generation.

## Important APIs, types, and functions

- Option key macros define stable CLI/config keys such as `VKEY_FEATURES_QUOTA`, `VKEY_CHANGELOG`, `VKEY_MARKER_XTIME`, `VKEY_FEATURES_BITROT`, `VKEY_PARALLEL_READDIR`, `VKEY_READDIR_AHEAD`, `VKEY_CONFIG_GFPROXY`, SSL option keys, auth map keys, and GNFS disable/auth option expansions.
- `glusterd_client_type_t` distinguishes trusted clients, ordinary clients, and trusted proxy clients; this drives credential inclusion and volfile path selection.
- `glusterd_graph_type_t` labels service graph contexts: rebalance, quotad, snapd, and shd. The implementation uses this to suppress or alter translators such as readdir-ahead in service graphs.
- `struct volgen_graph` wraps a `glusterfs_graph_t`, optional `errstr` output for validation, and graph type.
- `glusterd_graph_builder_t` and `glusterd_vol_graph_builder_t` abstract global and per-volume graph builders used by service management code.
- `COMPLETE_OPTION` is the shared option-name completion macro. It maps short names to fully qualified option keys, reports invalid entries, and frees completions.
- `gd_volopt_flags_t` marks options requiring force, options that enable or disable xlators, options affecting clients, and options that must never be reset.
- `glusterd_server_xlator_t` and `glusterd_client_xlator_t` identify supported server and client insertion points for debug/user translators.
- `option_type_t` distinguishes documented and hidden options, split between local volume options and global options.
- `vme_option_validation` and `struct volopt_map_entry` define the option-map schema: key, translator type, translator option name, default value, documentation type, flags, op-version, description, and custom validation function.
- `struct volgen_brick_xlator` pairs a brick graph builder callback with a debug insertion key; `struct nfs_opt` maps NFS wildcard option patterns to concrete per-volume option names.
- Creation APIs include `glusterd_create_volfiles`, `glusterd_create_volfiles_and_notify_services`, `generate_brick_volfiles`, `generate_client_volfiles`, `generate_snap_client_volfiles`, `generate_dummy_client_volfiles`, `glusterd_generate_client_per_brick_volfile`, `glusterd_create_rb_volfiles`, and `glusterd_delete_volfile`.
- Service builder APIs include `build_shd_graph`, `build_quotad_graph`, optional `build_nfs_graph`, `build_rebalance_volfile`, `build_bitd_graph`, `build_scrub_graph`, `glusterd_snapdsvc_create_volfile`, `glusterd_snapdsvc_generate_volfile`, `glusterd_generate_gfproxyd_volfile`, `glusterd_build_gfproxyd_volfile`, and `glusterd_shdsvc_generate_volfile`.
- Option and validation APIs include `glusterd_volinfo_get`, `glusterd_volinfo_get_boolean`, `glusterd_validate_globalopts`, `glusterd_check_globaloption`, `glusterd_check_voloption_flags`, `glusterd_is_valid_volfpath`, `glusterd_volopt_validate`, `gd_get_vmep`, `glusterd_get_op_version_from_vmep`, `gd_is_client_option`, `gd_is_xlator_option`, `gd_is_boolean_option`, and `_get_xlator_opt_key_from_vme`.
- XML help helpers (`init_sethelp_xml_doc`, `xml_add_volset_element`, `end_sethelp_xml_doc`) are available when libxml support is compiled in.

## Control flow

The header declares a layered control model. High-level operation code calls `glusterd_create_volfiles` or `glusterd_create_volfiles_and_notify_services` after volume metadata changes. Those functions delegate to brick, client, gfproxy, and SHD generation; service managers call global builders such as `build_quotad_graph`, `build_bitd_graph`, `build_scrub_graph`, and optional `build_nfs_graph`. Rebalance, snapd, and SHD have explicit per-volume entry points because their graphs are tied to one volume or one service instance.

Validation callers use the option helpers before committing a volume-set operation. They check whether an option is global or local, whether it has flags such as `VOLOPT_FLAG_FORCE` or `VOLOPT_FLAG_CLIENT_OPT`, whether the mapped translator option exists and has a boolean type, and then build candidate graphs through the implementation validators. Option completion supports CLI shorthand by expanding unique suffixes.

## State and persistence behavior

The header itself stores no runtime state, but it defines the state that `glusterd-volgen.c` persists into volfiles. `volgen_graph_t` owns a graph during construction and validation. `volopt_map_entry` entries describe how persistent volume dictionary keys become translator options, default values, op-version gates, and validation behavior. Client type and graph type enums influence which credentials, services, and performance translators are emitted.

Generated volfiles are source-of-truth runtime artifacts for bricks and clients after glusterd writes them. Functions that create volfiles must preserve path layout and option compatibility across op-version changes. Functions such as `glusterd_volinfo_get_boolean` read volume dictionaries plus defaults, so callers should not assume unset means disabled.

## Dependencies and integration points

The header conditionally depends on libxml writer types for XML option help. It includes `glusterd-messages.h` and uses Gluster core types such as `glusterfs_graph_t`, `dict_t`, `glusterd_volinfo_t`, `glusterd_brickinfo_t`, `gf_transport_type`, and `volume_option_type_t` through surrounding glusterd includes.

It is included by volume operation code, service helpers, option validation code, and any caller that needs to regenerate volfiles. The option-map metadata connects CLI-visible volume options to translator volume-option tables loaded at runtime. The service builder declarations connect volgen to quotad, shd, snapd, gfproxyd, NFS, bitrot, scrub, and rebalance service management.

## Risks and edge cases

- `COMPLETE_OPTION` is a macro with logging, allocation, frees, and early returns. It assumes the caller's return type and cleanup semantics match the macro body.
- `struct volopt_map_entry` maps user-facing keys to translator-specific options; mistakes in `voltype`, `option`, default `value`, flags, or op-version can generate invalid graphs or incorrectly accept/deny option changes.
- Option flags are used by external code to decide force requirements, client notification needs, reset behavior, and xlator topology changes. Missing flags can cause stale client volfiles or unsafe resets.
- Public prototypes expose many service-specific builders. Callers must pass correctly initialized `volgen_graph_t`, `dict_t`, and `glusterd_volinfo_t` objects, especially when graph type changes validation behavior.
- Conditional GNFS and libxml declarations mean build coverage must include both enabled and disabled configurations.
- `_get_xlator_opt_key_from_vme` and `_free_xlator_opt_key` have paired ownership behavior: some returned keys are allocated expansions while others point into map entries.

## Test signals

Compile tests should cover GNFS and non-GNFS builds, libxml and non-libxml builds, and all files including this header. Functional tests should verify option completion, global/local option classification, op-version lookup, client-option and xlator-option flags, boolean option detection through loaded translator option tables, volfile path validation for long brick paths, and successful volfile generation for each exported service builder. Regression tests should include options with `!` synthetic names, auth/NFS wildcard expansions, forced reset flags, and client-affecting options that require client volfile refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-volgen.h -->
