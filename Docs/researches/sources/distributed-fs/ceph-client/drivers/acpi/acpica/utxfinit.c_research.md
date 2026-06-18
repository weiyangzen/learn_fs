## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utxfinit.c

Purpose: `utxfinit.c` exposes the main ACPICA initialization sequence: early subsystem initialization, hardware/event enablement, and namespace/device object initialization.

Important APIs and functions: `acpi_initialize_subsystem` initializes the OS layer, global variables, internal mutexes, namespace root, and default `_OSI` interfaces. `acpi_enable_subsystem` completes ACPI hardware enablement: clears early initialization, maps FACS unless disabled, enables ACPI mode unless disabled, initializes events unless disabled, and installs SCI/global-lock handlers unless disabled. `acpi_initialize_objects` initializes namespace devices/regions unless disabled, purges caches, and sets `ACPI_INITIALIZED_OK`.

Control flow: each phase is ordered and returns immediately on failure with contextual diagnostics. Compile-time reduced-hardware and obsolete-behavior blocks remove hardware or old object initialization as appropriate. Flags such as `ACPI_NO_FACS_INIT`, `ACPI_NO_ACPI_ENABLE`, `ACPI_NO_EVENT_INIT`, `ACPI_NO_HANDLER_INIT`, `ACPI_NO_DEVICE_INIT`, and `ACPI_NO_ADDRESS_SPACE_INIT` gate work.

State and dependencies: persistent state includes `acpi_gbl_startup_flags`, `acpi_gbl_early_initialization`, FACS mapping, original ACPI mode, initialized locks, namespace root, event handlers, and caches. Dependencies span OS services, tables, hardware, events, namespace, debugger, and `_OSI` utilities.

Integration points: platform ACPI boot code calls these phases in order after table discovery/loading. Later public APIs assume successful completion and startup flags.

Risks: phase ordering is critical: methods may require hardware/events, and `_REG`/`_STA`/`_INI` run after handler setup. Partial failures can leave initialized components for termination paths to clean.

Test signals: each no-init flag combination, reduced-hardware builds, OS-layer failure, mutex failure, namespace root failure, FACS mapping failure, ACPI enable failure, event/handler failure, device init failure, cache purge, and final startup flag are important.
