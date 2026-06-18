## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmath.c

Purpose: `utmath.c` supplies ACPICA's portable 64-bit integer math helpers for multiplication, shifts, division, and modulo. It exists so ACPICA can run in 32-bit or freestanding environments that may not provide native 64-bit divide or double-width arithmetic.

Important APIs and functions: `acpi_ut_short_multiply`, `acpi_ut_short_shift_left`, `acpi_ut_short_shift_right`, `acpi_ut_short_divide`, and `acpi_ut_divide` return `acpi_status` and write optional output pointers. The file uses `uint64_overlay` to access high and low 32-bit halves when `ACPI_USE_NATIVE_MATH64` or `ACPI_USE_NATIVE_DIVIDE` are not enabled. The native branches directly use C operators.

Control flow: each helper validates only what matters to that operation, notably zero divisors in divide paths, then computes and conditionally stores requested quotient, remainder, product, or shift result. The non-native full divide has a fast 64-by-32 path and a normalized 64-by-64 path that estimates and corrects a 32-bit quotient.

State and dependencies: there is no persistent state. The code depends on ACPICA arithmetic macros such as `ACPI_DIV_64_BY_32`, `ACPI_SHIFT_RIGHT_64`, trace/error macros, and status values including `AE_AML_DIVIDE_BY_ZERO`.

Integration points: string parsing, printf formatting, AML arithmetic execution, and resource conversion code call these helpers where native arithmetic may not be available.

Risks: correctness is most sensitive in the non-native divide correction logic, shift count handling, and overflow truncation expectations. Native shifts do not mask count, so callers must avoid invalid C shift counts in native builds.

Test signals: divide-by-zero should return `AE_AML_DIVIDE_BY_ZERO`; native and non-native builds should agree for boundary values such as 0, 1, `UINT32_MAX`, `UINT64_MAX`, high-bit divisors, and shift counts around 0, 31, 32, 63, and 64.
