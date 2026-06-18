## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utstrsuppt.c

Purpose: `utstrsuppt.c` provides low-level support for ACPICA string-to-integer conversion, including base-specific conversion loops, prefix/whitespace handling, and overflow-checked multiply/add helpers.

Important APIs and functions: `acpi_ut_convert_octal_string`, `acpi_ut_convert_decimal_string`, and `acpi_ut_convert_hex_string` accumulate base 8/10/16 values and return base-specific overflow or bad-constant statuses in compiler builds. `acpi_ut_remove_leading_zeros`, `acpi_ut_remove_whitespace`, `acpi_ut_detect_hex_prefix`, `acpi_ut_remove_hex_prefix`, and `acpi_ut_detect_octal_prefix` mutate caller string pointers. Static `acpi_ut_insert_digit`, `acpi_ut_strtoul_multiply64`, and `acpi_ut_strtoul_add64` implement checked accumulation.

Control flow: each conversion walks until null or invalid character, validates the digit class, multiplies the current accumulator by base, adds the new digit, and stops on invalid input or overflow while returning the value accumulated so far.

State and dependencies: there is no local persistent state, but overflow checks consult `acpi_gbl_integer_bit_width` to enforce 32-bit limits when needed. The helpers depend on `acpi_ut_short_divide`, ASCII hex conversion, and C character classification.

Integration points: `utstrtoul64.c` builds ACPI runtime, compiler, debugger, and tool conversion semantics on top of these helpers. Predefined-name repair and table parsers also depend on consistent conversion behavior.

Risks: runtime and compiler builds intentionally differ on invalid digits. Functions mutate string pointers, so callers must pass writable pointer variables. Global integer width must be set correctly before conversions that should enforce 32-bit limits.

Test signals: whitespace-only strings, leading zeros, hex/octal prefixes, invalid digits by base, maximum 32-bit and 64-bit values, overflow by one digit, compiler versus runtime invalid-input behavior, and pointer advancement after prefix removal should be validated.
