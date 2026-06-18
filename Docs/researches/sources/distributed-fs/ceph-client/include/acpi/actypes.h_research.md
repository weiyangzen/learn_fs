# sources/distributed-fs/ceph-client/include/acpi/actypes.h

Purpose: Defines the common ACPICA scalar types, pointer/size/address abstractions, object model, event/status constants, operation-region identifiers, callback signatures, buffer conventions, and utility macros used by the ACPI core and OS integration layer.

Important APIs, types, and functions: Key exports include `acpi_status`, `acpi_name`, `acpi_string`, `acpi_handle`, `acpi_size`, `acpi_io_address`, `acpi_physical_address`, `union acpi_object`, `struct acpi_object_list`, `struct acpi_buffer`, `struct acpi_device_info`, handler typedefs such as `acpi_gpe_handler`, `acpi_notify_handler`, `acpi_adr_space_handler`, `acpi_walk_callback`, and `acpi_exception_handler`, plus constants for ACPI object types, S/D/C power states, notify codes, GPE dispatch flags, address-space IDs, PM bit-register IDs, and `_STA` bits.

Control flow: Compile-time control flow selects 32-bit or 64-bit ACPICA behavior from `ACPI_MACHINE_WIDTH`, optionally narrows physical addresses with `ACPI_32BIT_PHYSICAL_ADDRESS`, and redirects allocation macros to either no-allocation stubs, debug-tracking allocators, or OS services. Runtime behavior is encoded as callback contracts and macros such as `ACPI_TIME_AFTER`, pointer arithmetic helpers, name-segment comparison/copy, acquire/release buffer conventions, and `ACPI_ALLOCATE_BUFFER`.

State and persistence: The header owns no state but defines state shapes used everywhere: ACPI namespace object data, memory mappings, system statistics, device IDs, connection contexts, PCC/FFH region contexts, and memory-cache descriptors. These are transient kernel/ACPICA state rather than firmware persistence.

Dependencies and integration points: Requires the platform/compiler headers to define machine width, calling conventions, and compiler-dependent integer types. It underpins ACPICA interpreter, namespace, table, event, OS services, device enumeration, operation regions, and Linux ACPI driver interfaces.

Risks and test signals: Risks are machine-width mismatches, pointer truncation, accidental inclusion without platform setup, object type value drift, misaligned name operations on strict-alignment CPUs, and callback ABI mismatches. Test with 32-bit and 64-bit builds, ACPI disabled/enabled builds, ACPICA unit tests, object evaluation covering every `union acpi_object` variant, and compiler warnings around pointer casts and packed data.
