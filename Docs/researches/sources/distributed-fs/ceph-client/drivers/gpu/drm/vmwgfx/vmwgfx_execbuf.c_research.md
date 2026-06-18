# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_execbuf.c

## Purpose
`vmwgfx_execbuf.c` is the vmwgfx command-submission verifier and submitter. It accepts userspace SVGA3D command streams through `DRM_VMW_EXECBUF`, validates every command against the caller's objects and the virtual device capability set, builds resource and buffer validation lists, patches userspace handles into hardware ids, submits through either the legacy FIFO or command-buffer manager, and returns/imports/exports synchronization fences.

## Important APIs, Types, and Functions
- `struct vmw_relocation`, `struct vmw_resource_relocation`, and `enum vmw_resource_relocation_type` hold delayed BO/MOB/GMR and resource-id fixups. Resource relocations can rewrite ids, unconditional NOP a command, or conditionally NOP it if an evicted resource has no host id.
- `struct vmw_ctx_validation_info` tracks a context resource plus its current and staged binding state for this execbuf.
- `struct vmw_cmd_entry` and `vmw_cmd_entries[]` are the verifier dispatch table. Entries encode callback, userspace permission, and guest-backed object capability requirements.
- `vmw_execbuf_res_val_add()`, `vmw_cmd_res_check()`, `vmw_view_res_val_add()`, and `vmw_view_id_val_add()` are the main resource lookup/validation helpers.
- Command-specific validators such as `vmw_cmd_dma()`, `vmw_cmd_draw()`, `vmw_cmd_set_shader()`, `vmw_cmd_dx_view_define()`, `vmw_cmd_dx_set_vertex_buffers()`, and SM5 UAV/indirect validators check embedded ids, dimensions, capability gates, dirty flags, and binding side effects.
- `vmw_cmd_check_all()` walks the submitted byte stream, using `vmw_cmd_check()` for each command and rejecting size drift.
- `vmw_execbuf_process()` is the central orchestration path; `vmw_execbuf_ioctl()` is the DRM ioctl entry point.
- `vmw_execbuf_fence_commands()` and `vmw_execbuf_copy_fence_user()` integrate with `vmwgfx_fence.c` and sync-file fd export.
- `__vmw_execbuf_release_pinned_bo()` and `vmw_execbuf_release_pinned_bo()` flush and unpin the global query BO.

## Control Flow
`vmw_execbuf_ioctl()` checks ABI version, optionally waits on an imported sync-file fence, and calls `vmw_execbuf_process()`. Processing optionally allocates an output fence fd, copies userspace commands into a command-buffer allocation or a vmalloc bounce buffer, takes `cmdbuf_mutex`, initializes the shared `vmw_sw_context`, optionally ties a DX context, validates all commands, reserves resources and BOs, validates memory placement, rebinds context state under `binding_mutex`, submits through FIFO or cmdbuf, emits a fence marker, commits staged context bindings and staged command resources, fences validated BOs, copies fence information to userspace, installs exported fence fds, and finally drops references outside the command mutex.

Error flow backs off BO validation, reverts staged command resources, commits no binding changes, frees relocation lists, releases invalid pinned query state if needed, frees command-buffer headers, and returns the negative errno. The code explicitly treats fence-submit failure as mostly harmless because the fence send path synchronizes before reporting failure to userspace.

## State and Persistence Behavior
The file mutates long-lived driver state: context binding state, cotables, staged view/shader/stream-output resources, `dev_priv->pinned_bo`, `dummy_query_bo_pinned`, `query_cid`, `query_cid_valid`, command-buffer manager state, last known query MOB binding, and BO/resource dirty tracking. Userspace handles are not submitted directly; they are translated only after validation has established stable TTM resources and resource ids. No filesystem persistence exists, but command submissions persist in host-visible SVGA device state and vmwgfx resource managers.

## Dependencies and Integration Points
This file depends on TTM validation, vmwgfx resource managers, BO placement helpers, binding/cotable/view/shader/stream-output code, KMS cursor snooping, FIFO and command-buffer reservation helpers, `vmwgfx_fence.c`, Linux `dma_fence`/`sync_file`, and DRM file-private TTM object tables. It is a high-risk integration layer between untrusted DRM ioctls and the virtual SVGA hardware command processor.

## Risks
The verifier must stay byte-for-byte synchronized with the device parser; any size miscalculation, unchecked command body, or stale relocation can become a device error or privilege boundary issue. Lock ordering between `cmdbuf_mutex`, validation reservations, and `binding_mutex` is delicate. Query BO pinning has recovery paths but can stall while waiting for device idle. Capability gates for guest-backed, DX, SM4/SM5, and GL43 commands must match host behavior. Usercopy failures after fence creation require forced waits and handle cleanup to avoid leaving userspace unable to synchronize.

## Test Signals
Good tests exercise valid and invalid execbuf streams, command-size truncation, privileged command rejection, guest-backed versus legacy capability paths, DX context requirements, view/shader/resource lifetime across eviction, BO relocation into VRAM/GMR/MOB, imported and exported fence fds, fence copyout failure handling, query BO switching, and suspend/reset paths that release pinned query state. Kernel signals include `VMW_DEBUG_USER` messages, `MKSSTAT_KERN_EXECBUF`, absence of `WARN_ON` in context-cache paths, and no lockdep or dma_fence warnings.
