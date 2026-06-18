# sources/distributed-fs/ceph/src/rgw/rgw_website.cc

## Purpose
`rgw_website.cc` implements S3 bucket website configuration behavior: redirect rule matching/application, effective index-document key selection, JSON/XML dump/decode, and validation of website redirect/error rules.

## Important APIs, Types, and Functions
`RGWBWRoutingRuleCondition::check_key_condition()` matches prefixes. `RGWBWRoutingRule::apply_rule()` constructs redirect URLs from default or rule protocol/host and replacement key settings. `RGWBWRoutingRules` checks rules by key, error code, or both. `RGWBucketWebsiteConf::should_redirect()` handles redirect-all or routing rules. `get_effective_key()` maps empty, directory, pseudo-directory, and file keys to index documents. Dump/decode functions cover JSON and S3 XML shapes.

## Control Flow
Website request handling asks for effective keys when serving website endpoints and calls `should_redirect()` on errors or redirect-all configs. XML decode gives `RedirectAllRequestsTo` precedence; otherwise it decodes index, error, and routing rules.

## State and Persistence Behavior
The file mutates in-memory website config structs that are encoded by the header into bucket metadata. It does not directly perform I/O.

## Dependencies and Integration Points
Depends on RGW XML/JSON helpers, Formatter, and website config structs. Used by bucket website PUT/GET and website request routing.

## Risks
`should_redirect()` sets `redirect_all.http_redirect_code = 301` on the configuration object instead of only the local rule, creating side effects in a predicate-like method. Redirect code validation allows 301-399 for redirects and 400-599 for error conditions. `apply_rule()` does not escape generated key segments.

## Test Signals
Cover redirect-all, key+error matching, key-only mismatch, replacement prefix/key mutual exclusion, redirect code validation, index suffix for root/directory/file, XML round trips, JSON round trips, and side-effect-free redirect checks.
