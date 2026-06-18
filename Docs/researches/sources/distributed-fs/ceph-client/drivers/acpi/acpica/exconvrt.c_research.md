# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exconvrt.c

## Purpose
`exconvrt.c` implements AML object conversion rules among integer, buffer, and string objects, plus target-type conversion used by Store and target operands.

## Important APIs, Types, And Functions
Public executor APIs are `acpi_ex_convert_to_integer`, `acpi_ex_convert_to_buffer`, `acpi_ex_convert_to_string`, and `acpi_ex_convert_to_target_type`. Private `acpi_ex_convert_to_ascii` formats integers or bytes in decimal or hex. The code depends on `acpi_gbl_integer_byte_width`, `acpi_gbl_integer_bit_width`, conversion flags such as `ACPI_IMPLICIT_CONVERSION`, `ACPI_IMPLICIT_CONVERT_HEX`, and explicit decimal/hex conversion modes.

## Control Flow
Integer conversion returns integer operands unchanged, parses strings with explicit or implicit string-to-integer helpers, and converts buffers little-endian up to the current integer width. Buffer conversion returns buffers unchanged, copies integer bytes little-endian, or copies string bytes plus a null terminator. String conversion returns strings unchanged, formats integers as decimal, explicit hex with `0x`, or fixed-width implicit hex, and formats buffers as comma- or space-separated decimal/hex byte strings with `0x` prefixes for hex byte output. Target conversion first classifies the current AML argument kind: explicit/simple targets mostly reject type changes, store targets convert based on destination object type, and reference targets pass through. A failed explicit type mismatch is normalized to success so Store can overwrite the target with the source object.

## State And Persistence
Conversions allocate new operand objects unless the source already has the requested type. New buffers are marked `AOPOBJ_DATA_VALID`. No namespace state is changed directly, but target conversion controls what object later gets stored.

## Dependencies And Integration Points
This file is used by concatenation, logical comparisons, Store, field writes, and other executor opcode paths. It relies on utility numeric parsing/formatting helpers and object allocation/reference conventions.

## Risks
Buffer-to-integer conversion rejects zero-length buffers and truncates to integer width. String conversion length calculations must match emitted separators and prefixes. Some behavior intentionally preserves compatibility quirks, such as including the string null terminator in string-to-buffer conversion.

## Test Signals
Tests should cover implicit versus explicit string parsing, zero-length buffer rejection, little-endian buffer/integer conversion, 32-bit table truncation, decimal and hex string formatting, buffer byte separators, null-terminator inclusion, Store target conversions, and overwrite-on-type-mismatch behavior.
