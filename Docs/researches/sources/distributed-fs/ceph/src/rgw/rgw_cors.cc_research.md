# sources/distributed-fs/ceph/src/rgw/rgw_cors.cc

## Purpose
Implements the shared RGW CORS rule/configuration model used by S3 and Swift frontends. It serializes CORS state, builds rules from delimited header values, matches origins and headers including simple wildcard patterns, formats response headers, and removes origin-specific rules.

## Important APIs, types, and functions
`RGWCORSRule::create_rule()` validates origin/header names, parses method flags, optional exposed headers, and `MaxAgeSeconds`. `lowercase_http_attr()` normalizes HTTP header names for case-insensitive matching. `is_string_in_set()` implements exact, global wildcard, prefix wildcard, suffix wildcard, and single embedded wildcard matching. `is_header_allowed()`, `is_origin_present()`, `has_wildcard_origin()`, and `format_exp_headers()` are the runtime checks. `RGWCORSConfiguration::host_name_rule()` selects the first matching rule.

## Control flow
Admin/update paths construct rules, persist them via `encode()`, and later RGW request handling scans rules in list order for a matching origin and method/header set. Header matching lazily builds a lowercase cache from `allowed_hdrs` on first use.

## State and persistence
State lives in `RGWCORSRule` fields and `RGWCORSConfiguration::rules`, encoded into Ceph `bufferlist`s. `lowercase_allowed_hdrs` is derived cache only; changing `allowed_hdrs` requires discarding it.

## Dependencies and integration points
Uses Ceph encode/decode, `Formatter`, JSON helpers, debug logging, `for_each_substr()`, `get_str_list()`, and Boost string helpers. S3 XML and Swift adapters reuse this core.

## Risks and test signals
Risks include wildcard overmatching, empty or malformed delimiter input, stale lowercase cache, and response-header injection. Tests should cover exact/wildcard origin and header matches, invalid multiple `*`, newline escaping in exposed headers, encode/decode round trips, and deletion of the last origin in a rule.
