# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evmisc.c

## Purpose
Provides miscellaneous event-manager support: validation and asynchronous dispatch of Notify requests, and event subsystem termination for fixed events, GPEs, SCI handlers, global lock, handler storage, and legacy-mode restoration.

## Important APIs, Types, And Functions
- `acpi_ev_is_notify_object` restricts Notify targets to Device, Processor, and Thermal objects.
- `acpi_ev_queue_notify_request` selects system versus device notify lists, builds a notify generic state, and queues asynchronous dispatch if any global or local handler exists.
- `acpi_ev_notify_dispatch` invokes the global notify handler and local notify handler chain, then frees the notify state.
- `acpi_ev_terminate` disables fixed events and all GPEs, removes global lock and SCI handlers, deletes GPE handler storage, clears initialized state, and returns to legacy ACPI mode if necessary.

## Control Flow
Notify queueing rejects unsupported target node types, determines handler-list ID based on `notify_value <= ACPI_MAX_SYS_NOTIFY`, loads local handlers from the node's attached object, and returns success without work if no handler is present. If work is needed, it creates `ACPI_DESC_TYPE_STATE_NOTIFY`, records node/value/local/global handler state, and submits `acpi_ev_notify_dispatch` to the notify worker queue. Termination runs only initialized event disablement first, then always removes SCI handlers, walks GPE lists to free handler structures, and finally disables ACPI if original mode was legacy.

## State And Persistence
Notify state is transient generic-state storage passed to the worker. Persistent event state includes global notify handler arrays, per-object notify lists, fixed-event enable state, GPE block/handler state, global lock state, SCI handler lists, `acpi_gbl_events_initialized`, and original ACPI mode.

## Dependencies And Integration Points
Uses namespace attached objects, OS work queues, generic-state allocation, fixed-event APIs, GPE list walking, hardware GPE disable callbacks, global-lock removal, SCI removal, and ACPI mode switching. GPE implicit notify dispatch from `evgpe.c` queues through this file.

## Risks And Edge Cases
No-handler Notify is intentionally ignored rather than treated as an error. Asynchronous dispatch means handler lists must remain valid until queued work drains. Termination logs errors but continues because teardown must be best-effort. Notify type validation must match ACPI object semantics or firmware notifications may be dropped incorrectly.

## Test Signals
Signals include Device/Processor/Thermal Notify acceptance, other types returning `AE_TYPE`, correct system/device notify list selection, global and local handler invocation order, cleanup when `acpi_os_execute` fails, fixed/GPE disable attempts during termination, GPE handler memory free, and legacy-mode disable on shutdown.
