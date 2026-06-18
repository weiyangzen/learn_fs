# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uterror.c

Purpose: `uterror.c` centralizes ACPICA internal warning/error output for predefined method validation, namespace lookup failures, and method execution failures when error messages are enabled.

Important APIs/types/functions: `acpi_ut_predefined_warning()`, `acpi_ut_predefined_info()`, and `acpi_ut_predefined_bios_error()` emit one-time messages based on namespace node flags. `acpi_ut_prefixed_namespace_error()` builds a prefix+internal path and classifies lookup failures. `acpi_ut_method_error()` reports method-path failures with formatted exception names. An obsolete `acpi_ut_namespace_error()` remains behind `__OBSOLETE_FUNCTION`.

Control flow: Predefined messages suppress repeated output once `ANOBJ_EVALUATED` is set. Namespace error classification treats `AE_ALREADY_EXISTS` and `AE_NOT_FOUND` as BIOS errors, other lookup failures as ACPICA errors, then builds and frees a full path. Method error optionally resolves a relative path from a prefix node before printing the node pathname.

State and persistence behavior: It does not store persistent state, but behavior is gated by node flags set elsewhere. It allocates/frees temporary path strings for diagnostics.

Dependencies and integration points: It depends on namespace path builders/printers, exception formatting, ACPICA output redirection macros, and is called by namespace lookup, predefined validation, and method execution paths.

Risks and test signals: Risks include log suppression hiding repeated firmware issues, allocation failure while building paths, confusing BIOS-vs-ACPICA error classification, and disabled output under `ACPI_NO_ERROR_MESSAGES`. Tests should cover predefined message suppression, prefixed path construction, method errors with and without path resolution, exception name formatting, and builds with error messages compiled out.
