# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_resource_priv.h

Purpose: Private resource manager interface shared by vmwgfx resource implementations. It defines the common virtual-function tables for resources and the simple-resource helper abstraction.

Important APIs/types/functions: `enum vmw_cmdbuf_res_state` describes committed/add/delete state notifications for command-buffer managed resources. `struct vmw_user_resource_conv` maps TTM base-object types to `struct vmw_resource`. `struct vmw_res_func` is the central resource vtable: type, memory requirements, domain/busy-domain, eviction support, priority, create/destroy/bind/unbind callbacks, command-buffer commit notifications, dirty callbacks, and clean callback. `struct vmw_simple_resource_func` extends this for fixed-shape ioctl-created resources. `struct vmw_simple_resource` embeds `vmw_resource` plus a function table pointer.

Control flow: Resource implementation files declare static `vmw_res_func` or `vmw_simple_resource_func` tables and hand them to `vmw_resource_init()` or `vmw_simple_resource_create_ioctl()`. The generic resource layer calls these callbacks during validation, eviction, cleanup, and dirty synchronization.

State and persistence: The header defines shape but no storage. Persistent state lives in each resource object and the callback tables, which are typically static const.

Dependencies and integration points: It depends on `vmwgfx_drv.h`, TTM object types, and all resource implementations (`shader`, `surface`, `context`, `views`, simple states). Risks are contract-level: callback NULLability must match generic resource behavior, `needs_guest_memory` must be accurate for MOB attachment, and dirty callbacks must be internally consistent. Test signals include compile coverage for all resource vtables, validation/eviction of every resource type, simple resource create/lookup/free, and command-buffer resource add/delete notification.
