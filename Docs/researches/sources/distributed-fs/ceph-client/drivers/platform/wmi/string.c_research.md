# sources/distributed-fs/ceph-client/drivers/platform/wmi/string.c

Purpose: Provides public WMI string conversion helpers between `struct wmi_string` UTF-16LE buffers and UTF-8 byte strings.

Important APIs and types: `wmi_string_to_utf8s()` converts a WMI string to a NUL-terminated UTF-8 destination. `wmi_string_from_utf8s()` converts UTF-8 source bytes into a NUL-terminated WMI string with a little-endian byte-length field.

Control flow: To-UTF8 computes input code-point count from the little-endian length field, requires destination capacity for at least a NUL byte, calls `utf16s_to_utf8s()`, and appends NUL. From-UTF8 requires at least one UTF-16 slot, calls `utf8s_to_utf16s()` leaving room for NUL, verifies the byte length fits in `u16`, writes length, and appends the UTF-16 NUL.

State and persistence: Stateless; callers provide all storage. Resulting WMI strings can be persisted only if a caller sends them to firmware or stores them.

Dependencies and integration points: Depends on NLS UTF conversion helpers, endian helpers, and public `linux/wmi.h`. `ACPI_WMI` selects `NLS` in Kconfig to satisfy this.

Risks: The helpers trust the source `struct wmi_string` storage to be large enough for its length field; callers must validate buffer bounds. Invalid UTF-16 is ignored by conversion behavior rather than surfaced as a hard failure in all cases. Destination truncation is possible by design when buffers are too small.

Test signals: `wmi_string` KUnit suite covers ASCII, non-ASCII BMP characters, surrogate pairs, padded/oversized WMI strings, truncation behavior, invalid UTF-16 handling, invalid UTF-8 rejection, and required NUL termination.
