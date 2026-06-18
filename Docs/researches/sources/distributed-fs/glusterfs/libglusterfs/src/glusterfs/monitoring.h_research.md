# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/monitoring.h

Purpose: `monitoring.h` declares the small metrics-export entry point for GlusterFS runtime monitoring.

Important APIs and types: `GLUSTER_METRICS_DIR` is `/var/run/gluster/metrics`. `gf_monitor_metrics(glusterfs_ctx_t *ctx)` returns a `char *`, likely a generated metrics payload or path depending on implementation.

Control flow and state: no inline logic. Runtime behavior is deferred to the implementation and depends on `glusterfs_ctx_t`.

Dependencies and integration: it includes `glusterfs.h` for context types and integrates with translator `dump_metrics` hooks declared in `xlator.h`.

Risks: `/var/run` path assumptions can fail under containers, non-root services, or changed runtime directories. The returned `char *` ownership contract is not documented here, so callers must consult the implementation.

Test signals: monitoring tests should cover missing metrics directory, permission failures, empty graphs, translators with and without `dump_metrics`, and memory ownership of the returned string.
