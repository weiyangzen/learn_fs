# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_va.c

Purpose: Implements overlay/video-acceleration stream handles as simple vmwgfx resources.

Important APIs/types: `struct vmw_stream`, `va_stream_func`, `vmw_stream_claim_ioctl()`, `vmw_stream_unref_ioctl()`, and `vmw_user_stream_lookup()`.

Control flow: Claim delegates to simple-resource creation; init calls `vmw_overlay_claim()` and stores the hardware stream id. The set-argument callback returns the user handle. Unref drops the file reference. Lookup resolves the simple resource from a TTM object file, rewrites the id to the hardware stream id, and returns a refcounted resource.

State/persistence: Stores `vmw_simple_resource` and hardware `stream_id`. Hardware overlay state is claimed until destroy calls `vmw_overlay_unref()`.

Dependencies/integration: vmwgfx simple-resource helpers, TTM object files, overlay claim/unref functions, and DRM ioctl structs.

Risks/test signals: User handles differ from hardware ids, overlay unref failures only warn, and non-evictable no-memory resources can leak ids. Test claim/unref, invalid lookup, exhaustion, and teardown with live streams.
