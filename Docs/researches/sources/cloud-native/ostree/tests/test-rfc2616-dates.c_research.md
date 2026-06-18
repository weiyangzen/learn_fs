# sources/cloud-native/ostree/tests/test-rfc2616-dates.c

## Purpose
This C unit test validates private RFC 2616 HTTP date parsing used by OSTree date utilities.

## Important APIs, Types, And Functions
It tests `_ostree_parse_rfc2616_date_time()` from `ostree-date-utils-private.h` and uses `GDateTime`, `g_date_time_format_iso8601`, GLib version guards, and GLib test APIs.

## Control Flow
For GLib 2.62 or newer, the test loops over valid and invalid date strings. Each string is parsed once as a normal NUL-terminated buffer and once as a same-length non-NUL-terminated buffer. Valid dates are formatted to ISO 8601 and compared; invalid ones must return `NULL`. Older GLib versions skip because ISO formatting is unavailable.

## State And Persistence
There is no persistent state. All parsing happens in memory.

## Dependencies And Integration Points
This integrates OSTree's HTTP date parser with GLib date-time validation. It covers strict GMT-only HTTP-date format used by HTTP caching and summary freshness code.

## Risks
Date parsing must reject malformed separators, invalid weekdays/months, overlong fields, underflow/overflow values, and non-GMT timezones. Handling non-NUL buffers is important for parsing byte ranges from network responses.

## Test Signals
The GLib test path is `/ostree_parse_rfc2616_date_time`. It validates boundary dates `1970-01-01T00:00:00Z` and `9999-12-31T23:59:59Z` plus many invalid variants.
