# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_simple_resource.c

Purpose: Generic helper for ioctl-created simple resources whose type-specific behavior can be described by `struct vmw_simple_resource_func`. It avoids duplicating TTM base-object setup, resource initialization, handle return, lookup, and teardown code.

Important APIs/types/functions: `struct vmw_user_simple_resource` embeds a TTM base object and a variable-sized `vmw_simple_resource`. `vmw_simple_resource_create_ioctl()` allocates enough memory for the requested simple resource, initializes the generic resource, registers a user handle, and writes the handle back through the type-specific callback. `vmw_simple_resource_lookup()` validates handle type and returns a referenced `vmw_resource`. Private helpers include `vmw_simple_resource_init()`, `vmw_simple_resource_free()`, and `vmw_simple_resource_base_release()`.

Control flow: Create allocates `offsetof(..., simple) + func->size`, stores the function table, initializes the resource with immediate ID allocation, invokes the type-specific `init`, creates the TTM base object, and drops the local reference. Base-object release unrefs the embedded resource; final resource free releases memory with `ttm_base_object_kfree()`.

State and persistence: Persistent state is the TTM base object plus embedded resource and type-specific tail. Object lifetime is jointly controlled by TTM handle references and resource krefs. No global state is owned here.

Dependencies and integration points: Depends on `vmwgfx_resource_priv.h`, TTM object files/base objects, DRM file-private `tfile`, and resource vtables supplied by simple resource implementations. Risks include allocation-size correctness for variable tail objects, type mismatch handling, double-unref mistakes during failed base-object init, and immediate ID allocation for resources that may not need hardware state yet. Test signals: simple resource create ioctls for every user, invalid handle/type lookup, init failure cleanup, handle release, and resource destructor invocation.
