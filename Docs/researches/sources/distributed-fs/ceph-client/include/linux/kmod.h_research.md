# sources/distributed-fs/ceph-client/include/linux/kmod.h

## Purpose

`kmod.h` exposes the kernel module autoload request API. It lets subsystems ask userspace module loading infrastructure to run modprobe synchronously or asynchronously, with compile-time stubs when module support is disabled. The source was read as a complete 32-line file.

## Important APIs, Types, and Functions

Under `CONFIG_MODULES`, `__request_module()` is the printf-style backend. Macros `request_module()`, `request_module_nowait()`, and `try_then_request_module()` select wait behavior and retry an expression after requesting a module. Without module support, request functions return `-ENOSYS` and `try_then_request_module()` leaves the original expression unchanged.

## Control Flow

Callers typically try a lookup, request the module if the lookup fails, and then retry. Synchronous requests wait for modprobe exit; nowait requests just initiate the helper.

## State and Persistence Behavior

This header owns no state. Runtime state is in usermode-helper execution, module loader state, and loaded modules.

## Dependencies and Integration Points

It includes usermode helper, GFP, errno, compiler, workqueue, and sysctl headers. It integrates with subsystem autoload paths such as protocol families, filesystems, and device drivers.

## Risks and Edge Cases

Return status from modprobe is documented as usually not useful. Callers must avoid recursive module requests and must handle `-ENOSYS`. Format strings must not be user-controlled without validation.

## Test Signals

Module autoload tests, `request_module_nowait()` lifetime tests, recursion/rate-limit tests, disabled-module build coverage, and lookup-then-request retry tests are useful.
