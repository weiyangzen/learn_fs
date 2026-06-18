# sources/distributed-fs/ceph/src/rgw/rgw_cors_swift.h

## Purpose
Provides the Swift-facing CORS configuration adapter for RGW.

## Important APIs, types, and functions
`RGWCORSConfiguration_SWIFT` inherits `RGWCORSConfiguration` and exposes `create_update()`. It calls `RGWCORSRule::create_rule()` with `allowed_methods="*"`, then pushes the resulting rule to the front of the rule list.

## Control flow
Swift metadata update paths provide allow-origins, allow-headers, expose-headers, and max-age strings. The adapter validates and converts them into a common CORS rule. A failed conversion returns `-EINVAL`; success stacks the rule before older rules.

## State and persistence
No Swift-only state is stored. The created `RGWCORSRule` is persisted through the shared CORS configuration encoding.

## Dependencies and integration points
Includes shared CORS and Ceph string-list helpers. It is intentionally header-only because the adapter is a small wrapper.

## Risks and test signals
Since Swift grants all RGW CORS methods when CORS metadata is valid, tests should confirm this is intended for Swift semantics. Cover invalid origin/header strings, omitted optional headers, max-age parsing, and rule ordering after repeated updates.
