# sources/distributed-fs/ceph-client/include/acpi/platform/aczephyr.h

Purpose: Configures ACPICA for Zephyr builds with 64-bit width, single-threaded operation, native RSDP pointer use, system C library usage, and disabled ACPICA error/debug output.

Important APIs, types, and functions: Defines `ACPI_MACHINE_WIDTH`, `ACPI_NO_ERROR_MESSAGES`, `ACPI_USE_SYSTEM_CLIBRARY`, `ACPI_SINGLE_THREADED`, `ACPI_USE_NATIVE_RSDP_POINTER`, includes Zephyr kernel/device/fs/assert headers, and declares `acpi_enable_dbg_print(bool enable)`.

Control flow: Compile-time configuration only; runtime debug output can be toggled by the declared function.

State and persistence: No state in the header. Zephyr ACPICA runtime may maintain debug-print state behind `acpi_enable_dbg_print()`.

Dependencies and integration points: Depends on Zephyr kernel/device/filesystem/sys headers and C library headers. Integrates ACPICA with Zephyr’s platform layer.

Risks and test signals: Risks include hard-coded 64-bit assumptions, single-threaded ACPI in a multithreaded environment, and disabled diagnostics hiding firmware errors. Test Zephyr ACPICA builds, debug toggling, RSDP discovery, and table parsing on target platforms.
