# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exnames.c

## Purpose
`exnames.c` parses AML name strings from the byte stream into allocated ACPICA namestring buffers, including root prefixes, parent prefixes, dual-name and multi-name prefixes, null names, and field-name restrictions.

## Important APIs, Types, And Functions
The exported parser helper is `acpi_ex_get_name_string`. Private helpers are `acpi_ex_allocate_name_string` and `acpi_ex_name_segment`. It uses AML prefix opcodes, `ACPI_NAMESEG_SIZE`, `ACPI_UINT32_MAX` as the internal root-prefix sentinel, and `acpi_ut_valid_name_char`.

## Control Flow
Allocation computes enough space for root/parent prefixes, optional dual or multi prefix bytes, name segments, and the null terminator, then writes the prefix encoding into the output buffer. Segment parsing rejects a leading digit, consumes exactly four valid name characters, appends them to the output string, returns `AE_CTRL_PENDING` when the first byte is not a name, and returns `AE_AML_BAD_NAME` for partial segments. Full namestring parsing disallows prefixes for field-unit names and parses exactly one segment. Other names first consume root or repeated parent prefixes, then handle dual-name, multi-name, null-name, or single segment forms. If a prefix was consumed but no valid segment followed, pending status is upgraded to malformed-name failure. On success the function returns the allocated namestring and byte length consumed.

## State And Persistence
The parser allocates a namestring owned by the caller. It does not update namespace state; it only advances an AML pointer locally and reports the consumed length. On failure it frees any allocated buffer.

## Dependencies And Integration Points
This helper is used by AML scanner/interpreter code while loading or executing names. Namespace lookup happens later; this file only validates and formats raw AML namepath syntax.

## Risks
The allocated buffer is intentionally somewhat larger than necessary, so callers must rely on returned length/string rather than exact allocation size. Malformed AML can produce pending status, bad-name errors, or leading-digit diagnostics. Field-unit prefix rejection is important because field declarations use restricted names.

## Test Signals
Tests should cover root name, repeated parent prefixes, dual and multi names, null names, single segment names, field-unit names with and without illegal prefixes, leading-digit rejection, partial segment bad-name reporting, consumed length accuracy, and allocation-failure cleanup.
