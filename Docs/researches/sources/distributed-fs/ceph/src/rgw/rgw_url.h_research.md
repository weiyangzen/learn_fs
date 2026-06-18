# sources/distributed-fs/ceph/src/rgw/rgw_url.h

## Purpose
`rgw_url.h` declares RGW URL parsing helpers for authority and userinfo extraction.

## Important APIs, Types, and Functions
`parse_url_authority(url, host, user, password)` and `parse_url_userinfo(url, user, password)` return bool success and write extracted strings.

## Control Flow
Callers pass mutable string references and check the boolean return before using outputs.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Only includes `<string>`. Implementation uses Boost.URL. The helpers are suitable for config parsing without exposing Boost types to callers.

## Risks
The comment documents accepted schemes but enforcement is in callers, not this helper.

## Test Signals
Header-level tests should verify callers include it without Boost.URL headers and link against the implementation.
