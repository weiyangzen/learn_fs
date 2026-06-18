# sources/cloud-native/ostree/src/libostree/ostree-date-utils.c

## Purpose
This file implements a strict, locale-independent parser for the RFC 2616/RFC 1123 HTTP date form used in cache validators, for example `Wed, 21 Oct 2015 07:28:00 GMT`.

## Important APIs, Types, And Functions
`parse_uint()` parses exactly two or four ASCII decimal digits within a caller-specified range and rejects overflow, partial parses, and non-digits. `_ostree_parse_rfc2616_date_time()` validates fixed length `29`, checks day and month names against static English arrays, validates separators and timezone `GMT`, parses numeric fields, allows second `60` for leap seconds, and returns `g_date_time_new_utc()`.

## Control Flow, State, And Persistence
The parser is positional and fail-fast: every delimiter, token, and numeric range is checked before constructing the timestamp. It deliberately does not verify that the weekday matches the date. No state is persisted; successful parses are returned as UTC timestamps for fetch metadata.

## Dependencies And Integration Points
It uses GLib character/date APIs, `errno`, and `strncmp`. It integrates with HTTP fetcher implementations, especially curl’s `response_header_cb()`, to populate `out_last_modified`.

## Risks And Test Signals
Strict format support means valid HTTP-date alternatives from RFC 2616, such as RFC 850 or asctime forms, are rejected. Leap-second handling depends on GLib accepting second `60`; callers handle a `NULL` return as timestamp `0`. Tests should cover exact valid strings, bad length, invalid month/day tokens, bad timezone, range failures, nonmatching weekday acceptance, leap second behavior, and malformed separators.
