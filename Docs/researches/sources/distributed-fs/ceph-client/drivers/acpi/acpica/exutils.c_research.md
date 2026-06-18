# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exutils.c

## Purpose
`exutils.c` provides executor utility functions and defines AML globals. It manages interpreter/namespace mutex entry, 32-bit integer truncation, global-lock acquisition for field access, numeric formatting helpers, EISA/PCI ID string conversions, and operation-region space ID validation.

## Important APIs, Types, and Functions
Exports are `acpi_ex_enter_interpreter()`, `acpi_ex_exit_interpreter()`, `acpi_ex_truncate_for32bit_table()`, `acpi_ex_acquire_global_lock()`, `acpi_ex_release_global_lock()`, `acpi_ex_eisa_id_to_string()`, `acpi_ex_integer_to_string()`, `acpi_ex_pci_cls_to_string()`, and `acpi_is_valid_space_id()`. The local helper is `acpi_ex_digits_needed()`. It defines `DEFINE_AML_GLOBALS` before including AML headers.

## Control Flow, State, and Persistence
Interpreter entry acquires the interpreter mutex then namespace mutex; exit releases them in reverse order. Integer truncation masks values to 32 bits when executing 32-bit ACPI tables. Global-lock helpers only act when the field flags request `AlwaysLock`, using the global lock mutex and current thread ID. Formatting helpers convert integer IDs to ACPI-required strings using division, byte swapping, and hex conversion. Space validation rejects reserved predefined region IDs while allowing user-defined regions, data-table regions, and fixed hardware.

## Dependencies and Integration Points
These utilities are used throughout the executor, field access, and system wait paths. They integrate ACPICA mutexes, global lock objects, AML global declarations, ACPI table integer width state, and namespace/region validation.

## Risks and Test Signals
Risks include mutex acquisition order regressions, lock release imbalance, silent global-lock acquisition failures, 32-bit truncation in the wrong execution mode, buffer-size assumptions in string conversions, and rejecting valid OEM/user region IDs. Tests should cover nested interpreter entry assumptions, blocking paths that exit/reenter, 32-bit and 64-bit integer truncation, global-lock requested/unrequested field accesses, EISA/PCI/integer string known vectors, and space ID boundary values.
