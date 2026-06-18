<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h

Purpose: declares the kernel-side management-console device registration interface and helper macro for config-string assembly.

Important APIs/types/functions: `struct mconsole_entry` wraps a list node and copied `mc_request`. `struct mc_device` defines configurable device callbacks: `config`, `get_config`, `id`, and `remove`. `CONFIG_CHUNK()` appends config fragments while tracking required output size. `mconsole_register_dev()` is real when `CONFIG_MCONSOLE` is enabled and a stub otherwise.

Control flow: drivers such as line, UBD, and vector networking register `mc_device` instances; `mconsole_kern.c` later dispatches config/remove requests to them.

State and persistence: no state is instantiated here, but it defines the callback contract for runtime mconsole reconfiguration.

Dependencies and integration points: depends on Linux lists and `mconsole.h`. Used by console, serial, UBD, vector, and memory config code.

Risks: `CONFIG_CHUNK()` deliberately returns required size even when the destination buffer is too small; callers must honor that contract. Callback contexts are process-context according to the comment.

Test signals: compile with and without `CONFIG_MCONSOLE`, query config strings that require buffer growth, and exercise all registered device callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.h -->
