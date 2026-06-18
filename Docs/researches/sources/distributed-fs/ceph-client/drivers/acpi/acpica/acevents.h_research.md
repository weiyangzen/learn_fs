# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acevents.h

Purpose: declares ACPICA event support for fixed events, SCI dispatch, GPE management, global lock handling, notify queuing, address-space handler installation, operation-region initialization, and region setup.

Important APIs/functions: defines `ACPI_GPE_IS_POLLING_NEEDED` when enabled. Declarations include event initialization, SCI handler install/remove, fixed-event detect, notify queueing, global lock acquire/release, low-level GPE detect/enable/mask/reference/finish, GPE block create/delete/init/dispatch, GPE list utilities, region handler install/lookup, address-space dispatch, region attach/detach, `_REG` execution, default region setup callbacks, and termination.

Control flow: initialization installs SCI/GPE and region handlers. SCI dispatch detects fixed events and GPEs; each GPE invokes a method, handler, or implicit notify path. Region access dispatches through installed address-space handlers and setup contexts.

State and persistence: event state is in GPE blocks/registers/interrupt blocks, handler objects, notify queues, global lock globals, fixed-event handler arrays, and region contexts stored in operand objects.

Dependencies and integration: depends on namespace nodes, GPE structs from `aclocal.h`, operand objects, hardware access, and OS interrupt services. It connects AML `Notify`, `_Lxx`/`_Exx`, operation regions, fixed events, and Linux ACPI interrupt handling.

Risks: GPE reference counts and masks are concurrency-sensitive. Edge-triggered polling is conditional. Region handler lifetime can race table unload if locking is wrong. Global lock handling must preserve firmware handshake semantics.

Test signals: fixed-event detection, SCI storms, GPE method/handler dispatch, wake/runtime masks, GPE block hot-add/remove, `_REG` execution, region setup failures, reduced-hardware builds, and lockdep checks.
