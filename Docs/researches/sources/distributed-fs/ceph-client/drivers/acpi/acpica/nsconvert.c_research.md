<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c

## Purpose
Provides conversion helpers used by predefined-object repair. These routines turn common firmware return mistakes into the ACPI-specified object forms consumed by drivers.

## Important APIs, Types, And Functions
Exports internal converters `acpi_ns_convert_to_integer`, `acpi_ns_convert_to_string`, `acpi_ns_convert_to_buffer`, `acpi_ns_convert_to_unicode`, `acpi_ns_convert_to_resource`, and `acpi_ns_convert_to_reference`. They operate on `union acpi_operand_object`, namespace scopes, AML resource end tags, and reference objects.

## Control Flow
Integer conversion accepts strings parsed as integers and buffers up to 8 bytes interpreted little-endian. String conversion accepts integer zero as an empty string, nonzero integers through implicit hex conversion, and buffers copied until NUL. Buffer conversion accepts integers, strings, and packages of integer DWORDs. Unicode conversion leaves valid buffers alone or expands ASCII strings to UTF-16LE buffers. Resource conversion repairs null, zero, or empty returns into an end-tag resource template. Reference conversion internalizes a returned pathname string, looks it up relative to scope, and builds a named-reference object.

## State And Persistence
Creates new operand objects and may add a reference to a resolved namespace node's attached object for references. It does not install converted objects itself; callers replace or wrap return values.

## Dependencies And Integration Points
Used by `nsrepair.c` and return validation. Depends on interpreter conversion helpers, namespace lookup/internalization, resource descriptor constants, and object allocation/reference management.

## Risks And Edge Cases
Buffer-to-integer refuses buffers larger than 64 bits. Buffer-to-string truncates at first NUL. Package-to-buffer requires every element to be an integer. Reference conversion depends on correct scope search and can fail if firmware returns an invalid path.

## Test Signals
Cover each supported conversion, malformed numeric strings, oversized buffers, packages with null or non-integer elements, Unicode string/buffer returns, resource null/zero/empty repair, and `_DEP`-style string-to-reference resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsconvert.c -->
