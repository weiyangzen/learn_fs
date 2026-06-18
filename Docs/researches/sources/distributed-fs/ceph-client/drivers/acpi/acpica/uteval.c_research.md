# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uteval.c

Purpose: `uteval.c` provides common helpers for evaluating namespace objects/methods and validating their return types, especially standard device status and power methods.

Important APIs/types/functions: `acpi_ut_evaluate_object()` allocates `struct acpi_evaluate_info`, calls `acpi_ns_evaluate()`, checks expected return bitmaps, and returns an internal operand object. `acpi_ut_evaluate_numeric_object()` extracts an integer. `acpi_ut_execute_STA()` evaluates `_STA` with spec-defined defaults when missing. `acpi_ut_execute_power_methods()` evaluates arrays of `_SxD`/`_SxW`-style methods and returns byte values.

Control flow: Generic evaluation handles not-found as debug, other failures as method errors, rejects missing returns when expected, maps returned object types to `ACPI_BTYPE_*`, deletes unexpected implicit returns when interpreter slack is enabled and no return was expected, and removes references on type errors. Numeric/status/power wrappers call the generic helper and release returned objects after extracting values.

State and persistence behavior: It allocates temporary evaluation info and returns reference-counted operand objects to callers. `_STA` writes caller-provided flags; power methods fill an output byte array with values or `ACPI_UINT8_MAX` for missing/failed entries.

Dependencies and integration points: It depends on namespace evaluation, object reference deletion, method error reporting, type-name decoding, interpreter slack policy, standard method names, and is used by device enumeration/power management/ID helpers.

Risks and test signals: Risks include wrong expected-type bitmap, leaked return objects on wrapper errors, slack mode masking unexpected returns, default `_STA` behavior affecting device presence, and truncating power method integers to bytes. Tests should cover missing `_STA`, methods returning wrong types, no-return methods, implicit returns with slack on/off, mixed present/missing power methods, and allocation failure for evaluation info.
