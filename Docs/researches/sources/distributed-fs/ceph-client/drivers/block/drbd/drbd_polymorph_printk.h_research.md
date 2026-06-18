# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_polymorph_printk.h

## Purpose

`drbd_polymorph_printk.h` provides type-directed DRBD logging macros. Callers can pass a `drbd_device`, `drbd_peer_device`, `drbd_resource`, or `drbd_connection` pointer to one macro family and get a consistent log prefix that includes the relevant resource, volume, and minor context. The header also wraps dynamic debug support and provides DRBD assertion helpers.

## Important APIs, Types, And Functions

- `drbd_printk(level, obj, fmt, ...)` is the central polymorphic logging macro. It uses compile-time type selection to choose the right prefix preparation, format string, and argument list.
- `dynamic_drbd_dbg(obj, fmt, ...)` mirrors `drbd_printk` for dynamic debug.
- Convenience macros `drbd_emerg`, `drbd_alert`, `drbd_crit`, `drbd_err`, `drbd_warn`, `drbd_notice`, and `drbd_info` bind standard kernel log levels.
- `drbd_ratelimit` provides a static ratelimit state for repeated warnings.
- `D_ASSERT(x, exp)` logs a failed assertion without changing control flow.
- `expect(x, exp)` evaluates an expression, logs a ratelimited assertion failure if false, and returns the boolean result.
- `drbd_printk_with_wrong_object_type` and `drbd_dyn_dbg_with_wrong_object_type` are intentionally undefined/extern error targets for unsupported object types.

## Control Flow

Each supported DRBD object type has four helper macros: prep, format, args, and unprep. For a device or peer device, the prep block derives the backing `drbd_device` and `drbd_resource`, and the format includes `drbd resource/volume drbdminor`. For a resource or connection, the prefix is resource-oriented.

`drbd_printk` nests `__builtin_choose_expr` calls. Each branch first supplies a compile-time `__builtin_types_compatible_p` condition, then a statement expression that prepares context and calls `printk`. Because the choice is compile-time, unsupported object types fall through to the wrong-type symbol. Dynamic debug follows the same pattern but creates dynamic-debug metadata, checks `DYNAMIC_DEBUG_BRANCH`, and calls `__dynamic_pr_debug` only when enabled.

When `CONFIG_DYNAMIC_DEBUG` is absent, the header provides stub definitions that preserve compile-time references while making dynamic debug branches false and avoiding runtime output.

## State And Persistence Behavior

The header does not own persistent state. Its only local state is the static ratelimit state created inside `drbd_ratelimit`. Logging reads object fields such as `resource->name`, `device->vnr`, and `device->minor`, so call sites must pass live objects and hold whatever references or locks make those fields safe in context. Assertion helpers do not halt execution or mutate DRBD state.

## Dependencies And Integration Points

This header relies on GCC-style builtins and statement expressions, Linux `printk` log levels, dynamic debug macros, ratelimit APIs, and DRBD core structures. It is included by DRBD internals to standardize diagnostic output across resource-, connection-, device-, and peer-device-oriented code.

## Risks

- The polymorphism is compile-time macro machinery, so type qualifiers and pointer type mismatches matter. Passing a wrapper, void pointer, or stale pointer will either fail compilation through the wrong-type target or log invalid context.
- The prefix helpers dereference object relationships without NULL checks. Callers must not use these macros before object linkage is established or after teardown begins.
- Stubbed dynamic debug support must remain compatible with kernel dynamic-debug macro signatures; drift in upstream dynamic-debug APIs can break builds.
- `D_ASSERT` and `expect` are diagnostics, not enforcement. Code paths that require hard failure must not rely on them for safety.

## Test Signals

Build coverage is the primary signal: calls with each supported object pointer type should compile, and unsupported types should fail. Runtime tests can validate emitted prefixes for devices, peer devices, resources, and connections. Dynamic-debug builds should confirm disabled debug sites are quiet and enabled sites include the same contextual prefix. Ratelimit behavior can be observed by repeated `expect` failures.
