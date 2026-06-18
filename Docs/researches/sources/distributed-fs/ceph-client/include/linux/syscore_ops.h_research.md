<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscore_ops.h -->
# sources/distributed-fs/ceph-client/include/linux/syscore_ops.h

## Purpose

`syscore_ops.h` defines system-core operation registration for devices or subsystems that need very late suspend, early resume, or shutdown callbacks outside normal device PM ordering.

## Important APIs, types, and functions

`struct syscore_ops` provides `suspend`, `resume`, and `shutdown` callbacks taking opaque data. `struct syscore` stores list node, ops pointer, and data pointer. APIs are `register_syscore()`, `unregister_syscore()`, `syscore_suspend()`, `syscore_resume()` under `CONFIG_PM_SLEEP`, and `syscore_shutdown()`.

## Control flow

Subsystems register a `struct syscore`. During system sleep, PM core walks registered syscore objects after normal device suspend and invokes `suspend`; on resume it invokes `resume` early. Shutdown walks callbacks to quiesce core hardware. Unregister removes the object from the global list.

## State and persistence behavior

Registered syscore objects persist in a global list until unregister. Callback data is caller-owned and must outlive registration. Suspend failures affect PM unwind.

## Dependencies and integration points

It depends on lists and integrates with PM sleep core, shutdown paths, clocks/timers/interrupt controllers, and other fundamental subsystems that cannot rely solely on device PM.

## Risks and test signals

Risks include registering stack objects, wrong ordering assumptions, sleeping in late callbacks when not allowed, missing resume after failed suspend, and callbacks touching devices already suspended. Tests should cover registration/unregistration, suspend failure unwind, callback ordering, shutdown invocation, and builds without CONFIG_PM_SLEEP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscore_ops.h -->
