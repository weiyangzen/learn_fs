# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.cc

## Purpose
This file implements default sync module extension hooks, a coroutine for statting remote objects and invoking optional callbacks, and registration of built-in sync modules.

## Important APIs, Types, and Functions
- `RGWSyncModuleInstance::alloc_bucket_meta_handler()` returns the default bucket metadata handler.
- `RGWSyncModuleInstance::alloc_bucket_instance_meta_handler()` returns the default bucket-instance metadata handler.
- `RGWStatRemoteObjCBCR` captures stat results for callback subclasses.
- `RGWCallStatRemoteObjCR::operate()` stats a remote object, logs results, and optionally calls a callback allocated by `allocate_callback()`.
- `rgw_register_sync_modules()` registers built-in modules: `rgw` as default, `archive`, `log`, `elasticsearch`, and `cloud`.

## Control Flow
Sync module instances default to standard metadata handlers unless overridden. Remote stat flow runs as a coroutine: call lower-level remote stat, return on error, log successful metadata, allocate a callback, pass stat result state into it, and call it. Registration constructs shared module objects and registers each name with the manager.

## State and Persistence Behavior
The file does not persist state directly. Metadata handler allocation determines which handlers persist bucket metadata. Remote object stat results are held in coroutine fields and optionally passed to callbacks. Module registration stores shared module instances in the manager map.

## Dependencies and Integration Points
It depends on coroutine infrastructure, RADOS coroutine helpers, data sync context/environment, bucket metadata handlers, and built-in sync module headers for log, Elasticsearch, AWS/cloud, archive/default behavior. It integrates with `RGWSI_SyncModules` and service/control initialization.

## Risks
- Built-in module names are configuration-facing.
- `RGWCallStatRemoteObjCR` intentionally skips callback behavior when `allocate_callback()` returns null, which can hide expected subclass behavior.
- Callback coroutines receive moved attrs/headers, so later code must not expect local copies.

## Test Signals
Signals include sync module registration tests, default module lookup by empty name and `rgw`, custom module metadata handler override tests, and remote stat callback tests for success/error paths.
