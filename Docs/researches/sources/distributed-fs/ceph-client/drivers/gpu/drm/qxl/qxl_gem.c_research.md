# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_gem.c

Purpose: This file wraps QXL BO allocation in DRM GEM object lifecycle and handle management.

Important APIs, types, and functions: `qxl_gem_object_create()`, `qxl_gem_object_create_with_handle()`, `qxl_gem_object_free()`, `qxl_gem_object_open()`, `qxl_gem_object_close()`, `qxl_gem_init()`, and `qxl_gem_fini()`.

Control flow: Object creation aligns to at least a page, calls `qxl_bo_create()`, exposes the embedded TTM GEM object, and tracks the BO on `qdev->gem.objects` under `gem.mutex`. Handle creation creates a DRM handle and either returns the object reference to the caller or drops the allocation reference. Free evicts any QXL surface and finalizes the TTM BO; fini force-deletes still-active user objects.

State and persistence: Maintains the per-device GEM object list and per-object GEM/TTM references. Surface state can be torn down during free before TTM finalization.

Dependencies and integration points: Used by QXL ioctls, dumb creation, monitors object creation, and object funcs in `qxl_object.c`. Relies on DRM GEM handles, TTM BO lifecycle, and QXL surface eviction.

Risks: If `drm_gem_handle_create()` fails, the local object reference is not explicitly dropped in this function, which should be audited against DRM ownership expectations. Force-delete indicates userspace leaked objects and is a last-resort cleanup path. Open/close are no-ops, so per-file accounting is not tracked.

Test signals: GEM allocation and handle creation failures, object close/unload with live handles, debugfs GEM list consistency, and memory leak checks on driver unload.
