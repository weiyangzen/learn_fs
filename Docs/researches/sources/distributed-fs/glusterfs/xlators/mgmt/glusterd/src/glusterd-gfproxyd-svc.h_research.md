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
