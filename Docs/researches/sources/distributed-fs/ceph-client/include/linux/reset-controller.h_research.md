# sources/distributed-fs/ceph-client/include/linux/reset-controller.h

Purpose: this header declares the provider-side reset controller interface used by drivers that expose reset lines to other devices.

Important APIs/types/functions: `struct reset_control_ops` provides `reset`, `assert`, `deassert`, and `status` callbacks. `struct reset_controller_dev` stores ops, owner module, global/list state, requested reset-control list head, device and firmware nodes, OF/fwnode specifier cell counts, translation callbacks, reset count, and a mutex. Registration APIs are `reset_controller_register()`, `reset_controller_unregister()`, and `devm_reset_controller_register()`, with no-op stubs when reset controller support is disabled.

Control flow: a provider fills `reset_controller_dev`, including translation from firmware reset specifiers to numeric line IDs, then registers it. Consumers in `reset.h` acquire `struct reset_control` handles that call back into these ops. Unregistration removes the provider from the reset core and prevents new acquisitions.

State and persistence: provider state persists in `reset_controller_dev`, including a mutex-protected list of requested controls. Hardware reset-line state is external and represented through callbacks.

Dependencies and integration points: depends on lists, mutexes, modules, device tree, fwnode references, and the reset consumer API.

Risks: bad translation callbacks can route consumers to the wrong reset line. Providers must handle shared consumers and concurrent operations through reset core locking and their own hardware locking. Test signals include provider registration/unregistration, DT/fwnode translation, consumer get/assert/deassert/status paths, disabled-config builds, and devm cleanup.
