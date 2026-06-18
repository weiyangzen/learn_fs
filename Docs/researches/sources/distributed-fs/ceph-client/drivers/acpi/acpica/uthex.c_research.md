# sources/distributed-fs/ceph-client/drivers/acpi/acpica/uthex.c

Purpose: `uthex.c` supplies small hex/ASCII conversion helpers used by compiler, disassembler, parser, and utility code.

Important APIs/types/functions: `acpi_ut_hex_to_ascii_char()` extracts a 4-bit nibble at a bit position from a `u64` and returns uppercase ASCII. `acpi_ut_ascii_to_hex_byte()` converts exactly two hex characters into one byte, validating both with `isxdigit()`. `acpi_ut_ascii_char_to_hex()` converts one valid hex character to a nibble.

Control flow: ASCII-to-byte rejects either invalid digit with `AE_BAD_HEX_CONSTANT`; otherwise it combines low and high nibbles. Single-char conversion assumes the caller already validated the character and branches by ASCII range.

State and persistence behavior: It holds only a static hex lookup table and mutates only caller-provided return bytes.

Dependencies and integration points: It depends on shift helper `acpi_ut_short_shift_right()`, C character classification, and ACPICA status codes. It is used where AML/compiler text or binary encodings need deterministic hex conversion.

Risks and test signals: Risks include caller misuse of `acpi_ut_ascii_char_to_hex()` with invalid characters, locale/signedness issues around `isxdigit`, and bit-position assumptions. Tests should cover uppercase/lowercase digits, invalid pairs, all nibble positions in a `u64`, and byte conversion order.
