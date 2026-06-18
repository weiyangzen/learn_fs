# sources/distributed-fs/ceph-client/drivers/reset/core.c

Purpose: generic Linux reset controller framework implementation. It registers reset providers, resolves firmware reset references, manages reset-control lifetime, and exports consumer APIs for reset, assert, deassert, status, acquire/release, bulk, array, devm, and device reset helpers.

Important APIs/types/functions: `struct reset_control`, `struct reset_control_array`, `struct reset_gpio_lookup`, `reset_controller_register()`, `reset_controller_unregister()`, `devm_reset_controller_register()`, `reset_control_reset()`, `reset_control_assert()`, `reset_control_deassert()`, `reset_control_status()`, `reset_control_acquire()`, `reset_control_release()`, `__fwnode_reset_control_get()`, `__reset_control_get()`, bulk/devm helpers, `__device_reset()`, and `fwnode_reset_control_array_get()`.

Control flow: providers register `reset_controller_dev` instances on a global list. Consumers call get APIs; firmware references are resolved by name/index from `resets` or optional `reset-gpios`; the framework finds the provider, translates cells, creates/refcounts a `reset_control`, and enforces shared/exclusive semantics. Operations dereference the controller under SRCU, validate array/error/acquisition state, then call provider ops. Devm wrappers attach cleanup actions; bulk and array paths roll back partial failures.

State and persistence: global provider and reset-gpio lookup lists are protected by mutexes. Each handle stores `rcdev`, ID, kref, acquisition flags, shared counters, SRCU, and lock. State is runtime-only and removed or nulled on controller unregister.

Dependencies and integration: integrates OF/fwnode, ACPI `_RST`, auxiliary bus, GPIO descriptors/machine lookup, device links, devres, IDA, kref, SRCU, module ownership, and reset-controller provider ops.

Risks and test signals: concurrency around controller unregister, shared reset counter misuse, `reset-gpios` dynamic auxiliary creation, and optional semantics are high-risk. Test provider unregister with live consumers, shared reset protocols, bulk rollback, devm deasserted cleanup, ACPI reset path, GPIO fallback flags, and probe deferral when providers are absent.
