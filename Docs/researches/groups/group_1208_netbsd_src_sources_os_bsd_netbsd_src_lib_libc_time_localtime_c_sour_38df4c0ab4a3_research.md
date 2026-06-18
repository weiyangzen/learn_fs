# Group Research: group_1208_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_time_localtime_c_sour_38df4c0ab4a3

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/localtime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/localtime.c

## Purpose
NetBSD libc’s tzcode-derived core for timezone loading, POSIX `TZ` parsing, forward conversion from `time_t` to `struct tm`, reverse conversion from `struct tm` to `time_t`, leap-second conversion helpers, and libc timezone globals.

It implements or supports `tzset`, `tzsetwall`, `localtime`, `localtime_r`, `localtime_rz`, `gmtime`, `gmtime_r`, `offtime`, `offtime_r`, `mktime`, `mktime_z`, `timelocal`, `timelocal_z`, `timeoff`, `timegm`, `time2posix`, `posix2time`, `time2posix_z`, `posix2time_z`, `tzalloc`, `tzfree`, `tzgetname`, and `tzgetgmtoff`.

## Main Structures
- `struct state`: in-memory TZif/POSIX timezone state, including transition times, transition type indexes, time type records, abbreviation storage, leap-second records, and proleptic repeat flags.
- `struct ttinfo`: one local-time type, with UTC offset, DST flag, abbreviation index, and standard/UT transition indicators.
- `struct lsinfo`: leap-second transition and correction.
- `struct rule`: POSIX DST transition rule in Julian-day, day-of-year, or month-week-weekday form.
- Global state includes `lclptr`, `gmtptr`, cached `lcl_TZname`, `lcl_is_set`, and compatibility globals `tzname`, `timezone`, `daylight`, and optionally `altzone`.

## Timezone Loading
`tzloadbody` loads compiled TZif data. It:
- Resolves `TZDEFAULT`, `TZDIR`, absolute paths, relative zone names, and colon-prefixed `TZ` values.
- Applies privileged-execution hardening with `issetugid`, rejects unsafe absolute paths, guards relative `..` traversal, and avoids opening device files where possible.
- Uses conservative open flags such as close-on-exec, no controlling terminal, regular-file hints, and optional `openat`/`TZDIR` containment.
- Parses TZif v1/v2/v3-style blocks, validating counts against `TZ_MAX_*`.
- Reads transition times, transition type indexes, `ttinfo` entries, abbreviations, leap seconds, standard/wall indicators, and UT/local indicators.
- Discards transitions outside representable `time_t`, while preserving boundary behavior at `TIME_T_MIN`.
- Parses trailing POSIX TZ strings when present and extends future transitions.
- Scrubs invalid abbreviation characters and rejects overlong abbreviations.

`tzload` wraps `tzloadbody` with stack or heap local storage. `zoneinit` handles empty `TZ` as fast UTC-like mode, tries TZif loading, falls back to POSIX `TZ` parsing when appropriate, and scrubs abbreviations.

## POSIX TZ Parsing
The parser helpers `getzname`, `getqzname`, `getnum`, `getsecs`, `getoffset`, `getrule`, and `transtime` parse names, offsets, and DST rules. `tzparse` builds synthetic state:
- Supports quoted names like `<...>`.
- Accepts explicit or default DST offsets.
- Uses `TZDEFRULESTRING` when a DST abbreviation is present without rules.
- Generates transitions across `years_of_observations`.
- Marks states repeatable with `goback`/`goahead` when the generated range is safe.
- Reuses leap-second information from a base TZif state when extending loaded zones.

## Conversion Logic
`timesub` converts a `time_t` plus offset into `struct tm`. It handles leap corrections, Gregorian 400-year cycles, signed and unsigned `time_t`, weekday/year-day/month-day derivation, `tm_gmtoff`, and positive leap-second display as `tm_sec == 60`.

`localsub` chooses the applicable `ttinfo` by transition search, handles repeatable proleptic rules before and after explicit transition tables, delegates to `timesub`, sets `tm_isdst` and `tm_zone`, and optionally updates libc timezone globals.

`gmtsub` is the GMT/fixed-offset equivalent. `gmtcheck` lazily initializes GMT state through `gmtload`.

## Reverse Conversion
`mktime` and related APIs use `time1`, `time2`, and `time2sub`:
- Normalize out-of-range fields.
- Binary-search the entire `time_t` range.
- Retry with normalized seconds to accommodate leap-second inputs.
- Resolve requested `tm_isdst` by trying alternative known timezone offsets.
- Use `tm_gmtoff` as a checked heuristic when available.
- Return `EOVERFLOW` for unrepresentable values and `EINVAL` for invalid local times.

`timegm` copies input and calls `timeoff` with zero offset. `timelocal` forces unknown DST before calling `mktime`.

## Threading and libc Integration
Under `_REENTRANT`, the file enables locks, optional read/write locking, and thread-specific static `struct tm` storage. It exposes internal `__lcl_*` symbols used by related libc code such as `strftime.c`.

`tzset_unlocked` refreshes local timezone state inside a caller-held critical section, optionally checks whether TZif data changed, upgrades read locks to write locks, updates compatibility globals, and falls back to UTC or `-00` on load errors.

## Risks and Edge Cases
- Security-sensitive path handling around `TZ`, `TZDIR`, privileged execution, traversal, and device files.
- Heavy overflow sensitivity across unusual `time_t` widths, signedness, and epochs.
- Leap-second support affects both forward and reverse conversion.
- DST gap/fold behavior depends on heuristics and compile-time options.
- Compatibility globals are process-wide even though internal state is locked.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/localtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/private.h

## Purpose
Private portability/configuration header for NetBSD’s tzcode-derived time implementation. It defines feature defaults, namespace shims, integer/time bounds helpers, compiler attributes, calendar constants, gettext support, and declarations used by `localtime.c`, `strftime.c`, `strptime.c`, and `zdump.c`.

## Configuration and Portability
The header sets NetBSD-oriented defaults such as `TM_GMTOFF`, `TM_ZONE`, `STD_INSPIRED`, `NETBSD_INSPIRED`, `HAVE_LONG_DOUBLE`, and runtime leap-second support. It can include `nbtool_config.h` for host-tool builds.

It defines feature-test macros before system headers, including `_GNU_SOURCE`, `_POSIX_PTHREAD_SEMANTICS`, `__EXTENSIONS__`, Windows POSIX-name exposure, and `_TIME_BITS=64` when compatible with `_FILE_OFFSET_BITS=64`.

It supplies fallbacks or probes for `bool`, `static_assert`, C89 integer types, `strnlen`, `mempcpy`, `getopt`, `environ`, errno constants, C23 checked arithmetic, and compiler attributes.

## API and Namespace Support
`TZ_TIME_T` support allows building tzcode with a private `time_t` or nonstandard epoch. When active, standard APIs are macro-renamed to `tz_*` forms, including time conversion, formatting, timezone-object, and compatibility globals.

The header declares standard-like APIs, STD-inspired APIs such as `tzsetwall`, `offtime`, `timelocal`, `timeoff`, `time2posix`, and `posix2time`, plus NetBSD APIs such as `timezone_t`, `localtime_rz`, `mktime_z`, `tzalloc`, `tzfree`, `posix2time_z`, and `time2posix_z`.

## Integer and Calendar Helpers
Defines:
- `TYPE_BIT`, `TYPE_SIGNED`, `TWOS_COMPLEMENT`.
- `MAXVAL`, `MINVAL`, `TIME_T_MIN`, `TIME_T_MAX`.
- `INT_STRLEN_MAXIMUM`, `INDEX_MAX`, and `INITIALIZE`.
- `UNINIT_TRAP` for `mktime` heuristics.
- Calendar constants for seconds, minutes, hours, days, weeks, months, Gregorian repeats, epoch year/weekday, `TM_*` values, `isleap`, and `isleap_sum`.

These helpers are used for overflow-sensitive conversion in `localtime.c`, `%s` formatting in `strftime.c`, and range scanning in `zdump.c`.

## libc Hooks
Under `_LIBC`, it includes `reentrant.h` and declares shared symbols implemented by `localtime.c`: `__lcl_ptr`, `__lcl_get_monotonic_time`, `__lcl_lock`, `__lcl_unlock`, and `tzset_unlocked`.

## Risks and Edge Cases
- Include order matters because this header mutates feature macros, symbols, and type names.
- `TIME_T_MIN/MAX` depend on representation assumptions guarded by static assertions.
- `TZ_TIME_T` macro renaming can obscure actual symbol names during debugging.
- Defaults differ depending on libc, host-tool, and standalone builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/strftime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/strftime.c

## Purpose
NetBSD libc implementation of `strftime`, `strftime_l`, `strftime_z`, and `strftime_lz`, formatting `struct tm` values into bounded locale-aware strings with timezone and epoch-seconds support.

## Entry Points
- `strftime_z`: timezone-object formatting using the current locale.
- `strftime_lz`: timezone-object formatting with explicit locale.
- `strftime`: locks local timezone state, refreshes it through `tzset_unlocked`, and delegates to timezone-aware formatting.
- `strftime_l`: same as `strftime`, but with explicit locale.

Weak aliases are provided where supported.

## Formatting Engine
`_fmt` recursively scans the format string and writes into the caller buffer. Supported conversions include:
- Locale names and templates: `%A`, `%a`, `%B`, `%b`, `%h`, `%c`, `%x`, `%X`, `%r`.
- Numeric date/time fields: `%C`, `%d`, `%e`, `%F`, `%H`, `%I`, `%j`, `%k`, `%l`, `%M`, `%m`, `%R`, `%S`, `%T`, `%U`, `%W`, `%w`, `%u`, `%v`, `%Y`, `%y`.
- ISO week/year: `%V`, `%G`, `%g`.
- Timezone and epoch: `%Z`, `%z`, `%s`.
- Literals and spacing: `%%`, `%n`, `%t`, `%+`.
- Padding modifiers: `%-`, `%_`, `%0`.
- Alternative modifiers `%E` and `%O`, accepted for standards compatibility but limited by available locale data.

`_add` handles bounded string append. `_conv` formats integers through `snprintf_l`. `_yconv` makes `%C`, `%y`, and `%Y` compose consistently for negative and large years.

## Locale and Timezone Behavior
The file uses NetBSD `_TimeLocale` from `sys/localedef.h` via `_TIME_LOCALE(loc)` for day/month names, AM/PM strings, and date/time templates.

For `%Z`, it prefers `tm_zone` when available; otherwise it queries `tzgetname` on the timezone object. For `%z`, it prefers `tm_gmtoff`; otherwise it uses compatibility globals or derives the offset by comparing `mktime_z` and `timegm`.

For `%s`, it reconstructs `time_t` from the supplied `struct tm`. If native `mktime` might overflow, the file can include `localtime.c` internally with a widened `timex_t` path.

## Error Behavior
`strftime_lz` returns `0` and sets `errno = ERANGE` if the output buffer fills. On success, it restores the caller’s previous `errno`, null-terminates output, and returns the byte count excluding the terminator.

## Risks and Edge Cases
- `%s` can pull in a specialized internal `localtime.c` build.
- Public wrappers depend on `localtime.c` internal locking and timezone state.
- `%Z`/`%z` behavior depends on whether `tm_zone` and `tm_gmtoff` are valid.
- Alternate locale modifiers are parsed but not deeply localized beyond the available NetBSD locale structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/strftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/strptime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/strptime.c

## Purpose
NetBSD libc implementation of `strptime` and `strptime_l`, parsing formatted date/time text into a caller-provided `struct tm`.

## Entry Points
- `strptime`: delegates to `strptime_l` with the current locale.
- `strptime_l`: main parser using `_TimeLocale` data.

Weak aliases are provided where supported.

## Parser Behavior
The parser tracks supplied fields with flags for year, month, yday, mday, wday, and hour. This lets it derive missing fields after parsing, such as yday from month/day, month/day from yday, and weekday from year/yday.

It supports split-century parsing for `%C` plus `%y`, week offsets from `%U` and `%W`, alternative modifier validation for `%E`/`%O`, and timezone offset sign handling.

## Supported Conversions
Composite conversions recurse through fixed or locale formats: `%c`, `%D`, `%F`, `%R`, `%r`, `%T`, `%X`, and `%x`.

Elementary conversions include:
- Weekday/month names: `%A`, `%a`, `%B`, `%b`, `%h`.
- Year/century: `%C`, `%Y`, `%y`.
- Date/time fields: `%d`, `%e`, `%H`, `%k`, `%I`, `%l`, `%j`, `%M`, `%m`, `%p`, `%S`.
- Epoch seconds: `%s`, parsed as nonnegative `time_t` and converted via `localtime_r`.
- Week fields: `%U`, `%W`, `%w`, `%u`.
- ISO week/year placeholders: `%g`, `%G`, `%V`, parsed but not fully used to synthesize dates.
- Timezone: `%Z`, `%z`.
- Whitespace/literals: `%n`, `%t`, `%%`.

## Timezone Parsing
`%Z` and `%z` recognize:
- `Z`, `UTC`, `UT`, and `GMT`.
- Numeric offsets `+hh`, `+hhmm`, `+hh:mm`, and negative forms.
- RFC 822/RFC 2822 North American abbreviations.
- Nautical/military one-letter zones except `J`, with `J` treated as local time.
- Current `tzname` values after `tzset`.
- Named zones loaded through `tzalloc` in `fromzone`.

When possible, it fills `tm_gmtoff`, `tm_zone`, and `tm_isdst`. Some cases intentionally leave `tm_zone = NULL`.

## Helpers
- `conv_num`: bounded decimal parser whose upper limit controls digit count.
- `find_string`: case-insensitive match against full and abbreviated locale strings.
- `first_wday_of`: computes first weekday for a Gregorian year.
- `fromzone`: loads a named timezone and extracts offset information.

## Risks and Edge Cases
- `%G`, `%g`, and `%V` do not fully resolve ISO week dates.
- `%s` accepts only nonnegative epoch seconds and checks overflow.
- Composite recursion calls `strptime`, not `strptime_l`, so nested locale behavior can depend on current locale.
- `%Z` is permissive and can leave timezone fields only partially specified.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/strptime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/tzcode2netbsd -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/tzcode2netbsd

## Purpose
Small historical shell helper documenting an old workflow for converting an upstream tzcode distribution into NetBSD source-tree form.

## Behavior
It defines a `NOIMPORT` list of upstream files that NetBSD did not import directly, including upstream makefiles, manual pages, sample data, images, and obsolete documentation artifacts.

The destructive operations are commented out:
- `rm -f ${NOIMPORT}`
- Moving `tzfile.h` into `../../../include`

The active script only prints reminders to check `tzfile.h`, find the current upstream version in the Makefile, and note that NetBSD no longer uses this script for imports.

## Risks
As committed, it is non-mutating. If the commented commands were re-enabled without review, it could delete files from an extracted tzcode tree and move headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/tzcode2netbsd -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/zdump.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/zdump.c

## Purpose
Implementation of `zdump`, the timezone diagnostic utility for printing current zone times and transition tables.

## Command-Line Interface
Supports:
- `--version`
- `--help`
- `-c [L,]U`: limit by calendar years, default `-500` through `2500`.
- `-t [L,]U`: limit by raw seconds since 1970.
- `-i`: brief experimental transition format.
- `-v`: verbose transitions.
- `-V`: less verbose transitions.

Without `-i`, `-v`, or `-V`, it prints current time for each requested zone.

## Timezone Access
When `localtime_rz` is available, the utility uses timezone objects via `tzalloc`, `tzfree`, and `localtime_rz`. Otherwise it falls back to mutating process-global `TZ`, calling `tzset`, and using `localtime_r`.

`gmtzinit` creates a GMT timezone object where supported. `my_gmtime_r` uses that object or falls back to `gmtime_r`.

## Transition Discovery
Verbose modes:
- Convert year cuts with `yeartot`.
- Sample forward in half-day increments.
- Detect changes in localtime success, UTC offset, DST flag, or abbreviation.
- Use `hunt` to binary-search the exact transition boundary.
- Print records through `show` or `showtrans`.

`showextrema` handles changes near representable `time_t` extrema where local or GMT conversion starts or stops succeeding.

## Formatting Helpers
- `show`: prints zone name, UTC time, local time, abbreviation, DST flag, and GMT offset.
- `dumptime`: fixed English day/month formatting.
- `showtrans`: compact transition output.
- `istrftime`: wraps `strftime` and adds `%f` for quoted zone name, `%L` for local time, and `%Q` for offset/abbreviation/DST tuples.
- `format_local_time`, `format_utc_offset`, and `format_quoted_string`: compact machine-readable formatting.
- `tformat`: chooses the correct `printf` format for `time_t`.
- `saveabbr`: preserves abbreviations when fallback paths can overwrite `tzname`.

## Validation and Range Handling
`abbrok` warns once per zone for abbreviations with invalid characters, fewer than three characters, or more than six characters. Optional `TYPECHECK` verifies `localtime_rz` round-trips through `mktime_z`.

The utility computes native `time_t` extrema, uses 400-year Gregorian cycles in `yeartot`, and saturates cuts at representable bounds. Allocation helpers guard dynamic buffer growth and exit on size or memory failure.

## Risks and Edge Cases
- Fallback mode mutates process-global `TZ`.
- Half-day sampling assumes observable transition changes before binary refinement.
- Output buffers grow dynamically and exit on allocation failure.
- The code intentionally supports unusual `time_t` ranges and saturates year cuts at extrema.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/zdump.c -->