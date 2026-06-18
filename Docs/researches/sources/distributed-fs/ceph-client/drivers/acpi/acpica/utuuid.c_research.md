## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utuuid.c

Purpose: `utuuid.c` provides UUID conversion helpers for ACPICA compiler, acpi_exec, and help application builds. It converts between ACPI/ASL UUID strings and the 16-byte buffer layout used by `ToUUID`.

Important APIs and data: `acpi_gbl_map_to_uuid_offset[16]` maps each output buffer byte to the two hex characters in a canonical 36-byte UUID string. `acpi_ut_convert_string_to_uuid` converts a formatted UUID string into 16 bytes. `acpi_ut_convert_uuid_to_string` converts a 16-byte buffer back to canonical text with hyphens and null terminator.

Control flow: string-to-buffer conversion loops over all 16 bytes, reads two mapped hex characters, converts high and low nibbles with `acpi_ut_ascii_char_to_hex`, and stores the byte. Buffer-to-string loops over all bytes, writes high/low hex characters at mapped offsets with `acpi_ut_hex_to_ascii_char`, inserts four hyphens, and terminates.

State and dependencies: no mutable state. Compilation is limited to tool-like builds. The code depends on UUID length/offset constants and ACPICA hex conversion helpers.

Integration points: iASL `ToUUID` handling, acpi_exec, and help output use these conversions to match ACPI's specified byte ordering, which differs from simple left-to-right text order for the first UUID fields.

Risks: `acpi_ut_convert_string_to_uuid` assumes callers validated input length, hyphen positions, and hex characters. Buffer-to-string validates null pointers but assumes the output buffer is at least 37 bytes.

Test signals: canonical UUID round trips, mixed-case hex input, invalid/null pointer handling for buffer-to-string, mapped byte order for the first fields, and output hyphen/null placement should be checked.
