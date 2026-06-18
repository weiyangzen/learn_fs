# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_prime.c

Purpose: This file provides minimal PRIME/dma-buf hooks for QXL GEM objects, intentionally disabling cross-driver sharing while allowing local pin and vmap operations.

Important APIs, types, and functions: `qxl_gem_prime_pin()`, `qxl_gem_prime_unpin()`, `qxl_gem_prime_get_sg_table()`, `qxl_gem_prime_import_sg_table()`, `qxl_gem_prime_vmap()`, and `qxl_gem_prime_vunmap()`.

Control flow: Pin/unpin convert GEM to `qxl_bo` and call locked BO pin helpers. SG-table export and import return `-ENOSYS`, reflecting the comment that no other driver should share buffers with this virtual device. Vmap/vunmap call locked QXL BO map helpers.

State and persistence: No independent state. The functions alter BO pin count and map count/kptr through object helpers.

Dependencies and integration points: Hooked through `qxl_object_funcs` and the DRM driver `.gem_prime_import_sg_table`. Depends on callers holding the required reservation for locked pin/map operations.

Risks: The PRIME helpers use locked BO helpers directly; if DRM core invokes them without the BO reservation held, reservation assertions or races are possible. Returning `-ENOSYS` for sharing is intentional but limits dma-buf interoperability.

Test signals: PRIME import/export attempts should fail cleanly; local vmap/vunmap should maintain map_count; pin/unpin under dma-buf style paths should pass lockdep/reservation assertions.
