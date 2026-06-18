# sources/distributed-fs/ceph-client/drivers/platform/wmi/internal.h

Purpose: Declares private helper interfaces shared by WMI core implementation files.

Important APIs and types: Forward declares `union acpi_object` and `struct wmi_buffer`. Declares `wmi_unmarshal_acpi_object()` for converting ACPI return objects into WMI byte buffers, and `wmi_marshal_string()` for converting a WMI UTF-16LE string buffer into an ACPI string buffer.

Control flow: No executable control flow. `core.c` calls these helpers for newer typed WMI APIs; `marshalling.c` implements them; KUnit tests include the header.

State and persistence: No state. The header defines internal ABI between compilation units.

Dependencies and integration points: Included by `core.c`, `marshalling.c`, and `tests/marshalling_kunit.c`. It avoids exposing these helpers as normal public kernel APIs while still allowing KUnit visibility exports.

Risks: Signature changes must be synchronized across core, implementation, and tests. Because the helpers allocate output buffers, callers must keep ownership/freeing contracts consistent.

Test signals: Compile coverage of `wmi.o` and `wmi_marshalling_kunit`; namespace import for KUnit-only exports; callers freeing returned buffer data with `kfree()`.
