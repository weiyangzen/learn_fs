# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_streamoutput.c

Purpose: Manages DX stream-output objects as command-buffer-managed vmwgfx resources backed by MOB memory and registered in context cotables.

Important APIs/types: `struct vmw_dx_streamoutput`, `vmw_dx_streamoutput_add()`, `vmw_dx_streamoutput_remove()`, `vmw_dx_streamoutput_lookup()`, `vmw_dx_streamoutput_set_size()`, and `vmw_dx_streamoutput_cotable_list_scrub()`.

Control flow: Add allocates metadata, references the stream-output cotable, initializes a guest-memory resource, and stages it in the command-buffer manager. Commit notifications toggle `committed`, cotable list membership, and `res->id`. Bind/unscrub emits `DX_BIND_STREAMOUTPUT` with MOB id, offset, and size; unbind/scrub binds `SVGA3D_INVALID_ID`, removes cotable linkage, fences the BO, and clears the id.

State/persistence: Stores non-refcounted context, refcounted cotable, user key/id, size, cotable node, and committed flag. Hardware-visible binding persists until scrub or context teardown.

Dependencies/integration: Resource core, command-buffer resource manager, context cotables, `binding_mutex`, MOB-backed TTM resources, and SVGA DX commands.

Risks/test signals: Context lifetime ordering, synchronized `committed`/list/id state, non-MOB backing rejection, eviction/unbind, context destruction with live objects, and readback scrub behavior.
