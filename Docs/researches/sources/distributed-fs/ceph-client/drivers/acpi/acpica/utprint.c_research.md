## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utprint.c

Purpose: `utprint.c` implements ACPICA's bounded formatted-printing routines for environments where host libc behavior is unavailable or must be controlled. It supports `vsnprintf`, `snprintf`, `sprintf`, and application-only stdout/file wrappers.

Important APIs and functions: static helpers `acpi_ut_bound_string_length`, `acpi_ut_bound_string_output`, `acpi_ut_put_number`, and `acpi_ut_format_number` implement bounded string handling and integer formatting. `acpi_ut_scan_number` parses decimal width/precision fields. `acpi_ut_print_number` writes a decimal integer string. `vsnprintf` parses flags, width, precision, qualifiers, and specifiers. Application builds add `vprintf`, `printf`, `vfprintf`, and `fprintf`.

Control flow: `vsnprintf` walks the format string, emits ordinary characters through the bounded output helper, parses `%` flags, width, precision, and `h/l/ll` qualifiers, handles `%`, `%c`, `%s`, `%o`, `%x`, `%X`, `%d`, `%i`, `%u`, `%p`, and prints unknown formats literally. It always advances the logical output pointer even when the buffer boundary is reached, then null terminates if size is nonzero.

State and dependencies: no normal persistent state. Application output wrappers serialize use of `acpi_gbl_print_buffer` with `acpi_gbl_print_lock`. Number conversion depends on `acpi_ut_divide` and `acpi_ut_short_multiply`.

Integration points: ACPICA diagnostics, tools, debug paths, and string formatting in freestanding builds depend on this implementation.

Risks: return value semantics are the attempted length, not necessarily bytes stored. Supported specifiers are intentionally limited. Signed conversion casts through fixed widths, and pointer formatting defaults to zero-padded native pointer width.

Test signals: zero-size buffers, exact-fit truncation, width/precision combinations, left/zero padding, signed negatives, 64-bit `%ll` values, null `%s`, pointer formatting, literal `%%`, and application wrapper locking are key.
