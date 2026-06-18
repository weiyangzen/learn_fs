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
