# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxface.c

## Purpose
`evxface.c` exposes high-level ACPI event interfaces: notify handlers, SCI handlers, global and fixed event handlers, GPE handlers, and ACPI global lock acquisition/release. It is the host-facing registration surface that updates ACPICA event dispatch state.

## Important APIs, Types, And Functions
Exports include `acpi_install_notify_handler`, `acpi_remove_notify_handler`, `acpi_install_sci_handler`, `acpi_remove_sci_handler`, `acpi_install_global_event_handler`, `acpi_install_fixed_event_handler`, `acpi_remove_fixed_event_handler`, `acpi_install_gpe_handler`, `acpi_install_gpe_raw_handler`, `acpi_remove_gpe_handler`, `acpi_acquire_global_lock`, and `acpi_release_global_lock`. The internal `acpi_ev_install_gpe_handler` installs normal or raw GPE handlers. Important state includes `acpi_gbl_global_notify`, per-object `notify_list`, `acpi_gbl_sci_handler_list`, `acpi_gbl_fixed_event_handlers`, GPE dispatch flags, and `acpi_gbl_global_lock_mutex`.

## Control Flow
Notify installation validates the handle and handler type, creates an attached namespace object if needed, rejects duplicate handlers, and links a `LOCAL_NOTIFY` object into one or both notify lists. Notify removal unlinks under the namespace mutex, then waits for deferred notify tasks to finish before dropping references. SCI handler installation allocates a callback node, takes the events mutex plus GPE lock, rejects duplicate callbacks, and pushes the node onto the global list. Fixed event installation stores the handler before clearing/enabling the event; removal disables then clears the handler pointer. GPE handler installation allocates a handler object, validates the GPE, preserves original method/notify dispatch state, disables an auto-enabled method GPE if needed, and swaps dispatch to handler or raw-handler mode. Removal restores the original dispatch state, may re-enable a previously enabled method/notify GPE, waits for deferred GPE tasks, then frees the handler. Global lock operations enter the interpreter and delegate to executor mutex logic.

## State And Persistence
All state is in ACPICA globals or namespace-attached objects. Notify objects use ACPICA reference counts, including an extra reference when the same object is linked into both system and device lists. GPE handler install persists original flags and method node so removal can restore firmware dispatch. Global lock state persists in the global lock mutex and firmware global lock handle.

## Dependencies And Integration Points
This file integrates namespace validation, event mutexes, GPE spinlock-protected state, fixed event register helpers from `evxfevnt.c`, GPE runtime reference helpers from the event core, OS deferred-event completion waits, and executor mutex/global-lock code from `exmutex.c`.

## Risks
Lock ordering is central: namespace/events mutexes are combined with the GPE spinlock in several paths. Handler removal must wait for deferred work or freed handler objects could be used asynchronously. GPE handler installation can temporarily suppress firmware methods, so removal must faithfully restore method/notify dispatch and runtime references. Fixed handler installation does not validate a null handler beyond event range, so callers must pass usable callbacks.

## Test Signals
Tests should cover duplicate install rejection, root versus per-device notify behavior, all-notify reference accounting, deferred work drain on removal, fixed event enable/disable rollback, normal versus raw GPE dispatch flags, restoring original GPE method state, and global lock recursive acquisition by one thread.
