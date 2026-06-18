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
