<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h

## Purpose
Declares the generic i915 user-extension chain parser and callback type.

## Important APIs, types, and functions
- Forward declares `struct i915_user_extension`.
- `i915_user_extension_fn` callback receives the user extension pointer and caller data.
- `i915_user_extensions()` dispatches a chain through a callback table.

## Control flow
No implementation control flow exists in the header. It defines the callback contract for C files that parse UAPI extension chains.

## State and persistence
No state is stored here.

## Dependencies and integration points
Included by ioctl implementation files and implemented by `i915_user_extensions.c`.

## Risks
Callbacks receive user pointers and must perform their own safe copies for extension-specific payloads. Table count must correspond to the highest accepted UAPI name plus one.

## Test signals
Build coverage and ioctl extension parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h -->
