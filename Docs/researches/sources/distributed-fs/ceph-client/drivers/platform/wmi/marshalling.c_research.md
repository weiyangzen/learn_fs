# sources/distributed-fs/ceph-client/drivers/platform/wmi/marshalling.c

Purpose: Converts ACPI WMI method/data/event return objects into packed WMI buffers and marshals WMI UTF-16LE string buffers into ACPI ASCII strings for firmware calls.

Important APIs and types: `wmi_unmarshal_acpi_object()` is exported for KUnit and used by `core.c`; it supports ACPI integer, string, buffer, and one-level package objects. `wmi_marshal_string()` converts `struct wmi_string` input to `struct acpi_buffer`. Internal helpers compute aligned output sizes and copy simple objects.

Control flow: Unmarshal first computes total output length, aligning integers to 4 bytes and strings to 2 bytes, rejects unsupported/nested object types, enforces `min_size`, allocates zeroed memory with 8-byte-safe allocation sizing when needed, and transforms each object. Integers are emitted as little-endian 32-bit values, strings as WMI UTF-16LE strings with length and NUL terminator, and buffers as raw bytes. Marshal validates the WMI string header and length, requires an even byte count, rejects non-ASCII code units, stops at the first NUL to avoid copying padding, and returns an allocated ACPI string.

State and persistence: Stateless except for allocated output buffers. Callers own `buffer->data` or `out->pointer` and must free them.

Dependencies and integration points: Uses ACPI object types, WMI buffer/string definitions, overflow-safe size helpers, alignment macros, unaligned little-endian helpers, and KUnit visibility. It is central to `wmidev_invoke_method`, `wmidev_query_block`, event `notify_new`, and string-backed WMI methods.

Risks: ACPI integers are intentionally truncated to 32 bits despite possible 64-bit DSDT integers. Only ASCII strings can be marshalled into ACPI strings. Package handling is one-level only; nested packages fail. Size arithmetic and string length limits are security-sensitive because firmware controls return object shape.

Test signals: `wmi_marshalling` KUnit suite covers integer/string/buffer/package transforms, alignment, min-size rejection, nested/unsupported object rejection, invalid WMI string rejection, padded strings, and 8-byte allocation alignment.
