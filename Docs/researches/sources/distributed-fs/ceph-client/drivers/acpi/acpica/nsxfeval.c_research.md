# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfeval.c

## Purpose
`nsxfeval.c` contains public namespace evaluation and traversal interfaces. It resolves handles and paths, converts external parameters to internal ACPICA operands, evaluates methods or objects, converts internal returns back to `union acpi_object`, walks the namespace for clients, filters device enumeration, and exposes attach/detach/get data helpers.

## Important APIs, types, and functions
Exports include `acpi_evaluate_object_typed()`, `acpi_evaluate_object()`, `acpi_walk_namespace()`, `acpi_get_devices()`, `acpi_attach_data()`, `acpi_detach_data()`, `acpi_get_data_full()`, and `acpi_get_data()`. Internal helpers include `acpi_ns_resolve_references()` and `acpi_ns_get_device_callback()`. Key data types are `struct acpi_evaluate_info`, `struct acpi_object_list`, `struct acpi_buffer`, `struct acpi_get_devices_info`, ACPICA operand objects, and namespace nodes.

## Control flow
`acpi_evaluate_object_typed()` validates a return buffer, resolves a target handle for diagnostics, calls `acpi_evaluate_object()`, and validates the returned external object type unless the requested type is `ACPI_TYPE_ANY`. On type mismatch it frees an auto-allocated buffer and clears the buffer length. `acpi_evaluate_object()` allocates evaluation info, validates the prefix handle, handles absolute versus relative path rules, converts incoming external parameters into an internal null-terminated operand list, calls `acpi_ns_evaluate()`, and if a return buffer was provided, rejects namespace-node returns, dereferences simple `Index`/`RefOf` references, sizes the object, initializes the caller buffer, and copies the internal object outward. It then removes the internal return reference under interpreter lock and frees converted parameters.

`acpi_walk_namespace()` validates callbacks and depth, acquires the namespace read lock to protect against table unload, locks the namespace mutex, validates the start handle, and delegates to `acpi_ns_walk_namespace()` with callback unlocks enabled. `acpi_get_devices()` walks devices from root and filters through `acpi_ns_get_device_callback()`, which optionally matches `_HID` or `_CID`, runs `_STA`, prunes absent/nonfunctional devices, and invokes the user callback. Data attachment APIs lock the namespace, validate handles, then delegate to namespace attachment helpers.

## State and persistence behavior
Evaluation creates transient internal operand objects for parameters and return values. Return buffers may be caller-supplied or allocated by ACPICA. Attached data persists on namespace nodes until detached or node deletion and is keyed by handler. Namespace walking holds locks to prevent persistent namespace deletion while callbacks see nodes.

## Dependencies and integration points
This file bridges public ACPI exports to `acpi_ns_evaluate()`, namespace lookup/validation, object conversion (`acpi_ut_copy_eobject_to_iobject`, `acpi_ut_copy_iobject_to_eobject`), interpreter locking, `_HID`/`_CID`/`_STA` utility execution, namespace data attachment helpers, and Linux driver enumeration paths.

## Risks and edge cases
Parameter count is capped at `ACPI_METHOD_NUM_ARGS` with a warning, so excess caller arguments are silently ignored after logging. Reference returns inside packages are not recursively dereferenced. Device filtering intentionally avoids `_STA` until HID/CID match when a HID is requested, which changes side effects compared with unconditional `_STA`. Locking is subtle because callbacks may call ACPICA while table unload protection must remain in force. Auto-allocated buffers must be freed on typed-evaluation mismatch.

## Test signals
Evaluation tests should cover null and invalid handles, absolute/relative path rules, methods with zero and many arguments, excess argument warnings, no-return methods, typed return mismatch cleanup, `RefOf` and `Index` top-level returns, too-small return buffers, namespace-node return rejection, device HID/CID matching, `_STA` pruning, attach/detach/get data, and namespace walk callbacks that call back into ACPICA.
