# File Research: sources/block-storage/util-linux/sys-utils/hwclock-parse-date.y

Purpose: Provides the GPLv3 gnulib-derived date parser used by `hwclock --date` and `--predict` when `USE_HWCLOCK_GPLv3_DATETIME` is enabled.

Core behavior:
- Defines a reentrant Bison grammar for absolute times, ISO-8601 dates/times, numeric epochs using `@seconds`, month/day names, weekdays, timezone names and offsets, local time zone abbreviations, relative units, "ago"/"hence", and hybrid numeric date plus relative-offset input.
- Accumulates parse state in `parser_control`, including absolute date/time fields, relative year/month/day/hour/minute/second/nanosecond offsets, timezone selection, meridian style, and counters used to reject conflicting date/time constructs.
- Lexes signed/unsigned integers and decimal seconds with overflow checks and nanosecond truncation toward negative infinity for negative fractional values.
- Builds local timezone abbreviation tables from `tm_zone` or `tzname`, probing future quarters to detect alternate DST names where possible.
- Temporarily honors leading `TZ="..."` strings by mutating the process `TZ` environment for parsing and restoring the prior setting before returning.
- Converts parsed values through `mktime()`, applies weekday and relative date shifts, adjusts explicit time zones, then applies relative smaller units with overflow checks.

Important implementation details:
- The grammar explicitly expects 31 shift/reduce conflicts inherited from gnulib.
- `time_zone_hhmm()` accepts `HHMM`, `HH:MM`, and short hour forms with range checks against POSIX/ISO-style offset bounds.
- `to_year()` maps two-digit years 00-68 to 2000-2068 and 69-99 to 1969-1999.
- `mktime_ok()` guards against normalized invalid calendar fields and avoids false failure for valid timestamps equal to `(time_t)-1`.

Dependencies and integration:
- Includes util-linux `timeutils.h`, `cctype.h`, `nls.h`, and `hwclock.h`.
- `hwclock.c` calls `parse_date()` for `--date`/`--predict` under the GPLv3 parser build option.

Risks and edge cases:
- File comments note incomplete arithmetic overflow coverage and assumptions inherited from old gnulib code.
- `parse_date()` manipulates global timezone state, so the parser is reentrant at the Bison state level but not fully thread-isolated around TZ/localtime behavior.
- Timezone abbreviations remain inherently ambiguous; numeric offsets are more deterministic.
