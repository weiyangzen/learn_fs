# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.h

## Purpose
This header defines the per-file i915 DRM client accounting object and its reference/accounting API. It is the contract between file-private setup, GEM context lifecycle, internal GEM object attribution, and fdinfo reporting.

## Important APIs, Types, and Functions
`struct i915_drm_client` contains a `kref`, `ctx_lock`, `ctx_list`, optional `objects_lock` and `objects_list`, and `atomic64_t past_runtime[]` indexed through `I915_LAST_UABI_ENGINE_CLASS`. Inline helpers are `i915_drm_client_get()` and `i915_drm_client_put()`. Declared functions allocate/free clients, print fdinfo, and add/remove internal objects or context objects, with no-op inline stubs when `CONFIG_PROC_FS` is disabled.

## Control Flow
There is no executable flow beyond the inlines. Client users take references when linking objects, drop them when unlinking, and use `i915_drm_client_fdinfo()` from DRM fdinfo callbacks. Conditional stubs let non-proc builds compile without object attribution work.

## State and Persistence Behavior
The structure persists per DRM file and owns lists of live contexts and optionally client-attributed objects. Closed context runtime is retained in `past_runtime[]` after live context objects disappear.

## Dependencies and Integration Points
The header includes UAPI engine class definitions, GEM object types, Intel context types, and file-private declarations. It integrates `i915_file_private.h`, GEM context/object code, and DRM printers.

## Risks
Array sizing depends on `I915_LAST_UABI_ENGINE_CLASS` matching the highest class used by UAPI. The context and object lists require their documented locks/RCU rules. Adding fields here affects every open DRM file and should be weighed for memory footprint.

## Test Signals
Build with and without `CONFIG_PROC_FS`, fdinfo output under active workloads, object attribution for context state/rings, client cleanup after file close, and lockdep coverage for `ctx_lock` and `objects_lock`.
