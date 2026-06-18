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
