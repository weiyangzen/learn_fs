# sources/distributed-fs/ceph/src/rgw/rgw_arn.cc

## Purpose
Implements AWS-style ARN parsing, formatting, construction from RGW buckets/objects/IAM resources, wildcard matching, ordering, and ARN resource parsing.

## Important APIs, Types, and Functions
- `to_partition()` and `to_service()` convert parsed strings to enums, with optional wildcard support.
- `ARN::parse()` parses full ARN strings with or without wildcard acceptance.
- `ARN::to_string()`, `operator==`, and `operator<` provide value semantics.
- `ARN::match()` treats `this` as a wildcard-capable pattern.
- `ARNResource::parse()` and `to_string()` handle the resource segment.

## Control Flow
Parsing uses one of two static regexes depending on wildcard support. If the whole string is `*` and wildcards are allowed, it returns a fully wildcard ARN. Otherwise it validates partition and service values, then stores raw region/account/resource strings. Matching rejects wildcard candidates, checks partition/service with enum wildcards, then applies RGW wildcard matching to region, account, and resource.

## State and Persistence
No durable state. ARN objects are value types embedded in policy/account/role logic elsewhere.

## Dependencies and Integration Points
Depends on `rgw_common.h` for wildcard matching and RGW bucket/object types for constructors. Used by IAM, account root ARNs, role/policy logic, and S3 resource policies.

## Risks and Edge Cases
The `operator<` implementation compares fields with OR instead of lexicographic tie-breaking, so it can violate strict weak ordering for some combinations. Service mapping must be kept current for accepted AWS service names. Wildcard case-insensitivity applies to region/account but not resource.

## Test Signals
Tests should cover every supported partition/service, wildcard parse/match, invalid services, bucket/object constructors, ARNResource separator variants, strict weak ordering behavior, and case-sensitive resource matching.
