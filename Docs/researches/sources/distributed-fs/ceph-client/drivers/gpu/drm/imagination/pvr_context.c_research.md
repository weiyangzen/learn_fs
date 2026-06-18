# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.c

Purpose: implements userspace-visible PowerVR context creation, destruction, queue setup, firmware-context allocation, and context lifetime management.

Important APIs/functions: `pvr_context_create()` validates UAPI args, maps priority, looks up VM context, creates job queues, initializes firmware data, creates a firmware object, allocates firmware/global and per-file IDs, and returns a handle. `pvr_context_destroy()` removes a file handle, kills queues, and drops the handle reference. `pvr_destroy_contexts_for_file()` cleans all contexts on file close and unmaps VM state for still-referenced contexts. `pvr_context_device_init()`/`fini()` manage device context xarray and lock. Internal helpers initialize render/compute/transfer firmware data from static context streams and create/destroy/kill queues by context type.

Control flow and state: `struct pvr_context` is kref-managed. Device-wide `ctx_ids` provides firmware IDs; file `ctx_handles` provides user handles; `file_link` is protected by `ctx_list_lock`. Render contexts own geometry and fragment queues, compute contexts own one compute queue, transfer-frag contexts own one transfer queue.

Dependencies and integration: depends on DRM auth for high priority, stream parsing, firmware objects, queue creation, VM contexts, xarrays, krefs, and UAPI context/job types.

Risks: `pvr_context_lookup_id()` assumes `xa_load()` returns non-NULL before `kref_get_unless_zero()`, so callers must pass valid IDs or this path is fragile. The error path after firmware object creation goes to `err_free_ctx_data` rather than `err_destroy_queues`, which is worth reviewing for queue leakage. Priority elevation is gated by `CAP_SYS_NICE` or DRM master.

Test signals: create/destroy ioctls for all context types, invalid static-state lengths, close-time cleanup, high-priority permission tests, and queue teardown under outstanding references.
