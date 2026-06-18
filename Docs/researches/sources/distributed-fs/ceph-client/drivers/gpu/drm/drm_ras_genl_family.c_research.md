# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ras_genl_family.c

Purpose: wraps registration and unregistration of the generated DRM RAS Generic Netlink family.

Important APIs/types/functions: static `registered` records whether `genl_register_family()` succeeded. `drm_ras_genl_family_register()` registers `drm_ras_nl_family`; `drm_ras_genl_family_unregister()` unregisters it if currently registered.

Control flow: register clears `registered`, calls Generic Netlink registration, and sets `registered` only on success. Unregister tests the flag, unregisters the family, and clears the flag, making exit callable after failed init.

State and persistence behavior: one file-local boolean persists family registration state for DRM core init/exit.

Dependencies and integration points: depends on `drm_ras_genl_family.h`, generated `drm_ras_nl_family`, and DRM driver core init/exit ordering.

Risks: no locking protects `registered`, so the functions assume single-threaded core init/exit. The generated family object must remain initialized for the life of registration.

Test signals: init success, init failure injection, exit after failed init, double-exit no-op behavior, and netlink family visibility after registration.
