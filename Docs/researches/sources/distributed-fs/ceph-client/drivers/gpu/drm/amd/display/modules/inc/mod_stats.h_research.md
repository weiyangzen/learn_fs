# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_stats.h

Purpose: declares an opaque statistics module interface for display events, flips, vupdates, and FreeSync metrics.

Important APIs/types: `struct mod_stats` is opaque; `struct mod_stats_caps` is currently a dummy capability structure; `struct mod_stats_init_params` carries enable and entry-count configuration. Functions include create/destroy, init, dump, reset, event update, flip/vupdate timestamp update, and FreeSync metric update.

Control flow role: display code creates the module with a DC pointer and initialization parameters, then records events over time and optionally dumps or resets collected data.

State and persistence: actual storage is implementation-owned. Inputs include event strings, timestamps in ns, vtotal min/max, event trigger flags, window bounds, LFC midpoint, inserted frame count, and inserted frame duration.

Dependencies and integration: includes `dm_services.h` for DC/service types. It is designed as a low-friction telemetry hook for display timing and FreeSync behavior.

Risks: header exposes lengths and raw string pointers, so implementation must validate input length and lifetime. Timestamp units must stay consistent. Dummy caps may hide missing feature negotiation.

Test signals: create/init/destroy lifecycle, disabled stats behavior, event length boundaries, monotonic timestamp handling, reset after updates, and FreeSync metric formatting/dump output.
