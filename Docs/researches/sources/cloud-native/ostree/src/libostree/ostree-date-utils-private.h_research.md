# sources/cloud-native/ostree/src/libostree/ostree-date-utils-private.h

## Purpose
This private header exposes `_ostree_parse_rfc2616_date_time()` to non-introspection builds. It is used by HTTP fetcher code to parse cache-related `Last-Modified` header values without depending on locale-sensitive parsing.

## Important APIs, Types, And Functions
The single API is `GDateTime *_ostree_parse_rfc2616_date_time (const char *buf, size_t len)`. It returns a UTC `GDateTime` on success and `NULL` on malformed input.

## Control Flow, State, And Persistence
The header holds no state. It constrains call sites to provide an explicit byte length, which matters for parsing HTTP header substrings that may not be independently NUL-terminated or may include stripped CRLF.

## Dependencies And Integration Points
It depends on GLib and is hidden behind `#ifndef __GI_SCANNER__`, signalling internal C-only use. The curl fetcher includes it to convert `Last-Modified` response headers into Unix timestamps returned through fetch completion APIs.

## Risks And Test Signals
The risk is accidental exposure or ABI assumptions around a private helper. Tests should validate that users of this header treat `NULL` as a parse failure and do not dereference the result blindly.
