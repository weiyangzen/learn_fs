# sources/distributed-fs/ceph/src/rgw/rgw_string.cc

## Purpose
`rgw_string.cc` implements wildcard matching for RGW string utilities.

## Important APIs, Types, and Functions
`match_wildcards(pattern, input, flags)` maps RGW's `MATCH_CASE_INSENSITIVE` flag to `FNM_CASEFOLD` and delegates matching to libc `fnmatch()`.

## Control Flow
The function builds the `fnmatch()` flag word, calls `fnmatch(pattern.data(), input.data(), flag)`, and returns true only on exact match success.

## State and Persistence Behavior
The file is stateless and has no persistence side effects.

## Dependencies and Integration Points
It depends on `rgw_string.h` and `<fnmatch.h>`. Callers use it for glob-style matching of RGW policy/configuration strings.

## Risks
`std::string::data()` is expected to be null-terminated in modern C++; older assumptions would be risky. Behavior follows platform `fnmatch()`, including escaping and path-separator semantics. Case folding depends on `FNM_CASEFOLD` availability.

## Test Signals
Cover `*`, `?`, empty strings, literal metacharacters, case-sensitive and insensitive matches, and platform behavior for path separators.
