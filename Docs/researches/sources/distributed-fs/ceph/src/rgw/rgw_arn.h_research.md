# sources/distributed-fs/ceph/src/rgw/rgw_arn.h

## Purpose
Declares ARN value types and enum domains for RGW's AWS-compatible identity/resource policy handling.

## Important APIs, Types, and Functions
- `Partition` enumerates AWS partitions plus wildcard.
- `Service` enumerates accepted AWS service names plus wildcard.
- `ARN` stores partition, service, region, account, and resource; supports parsing, formatting, and pattern matching.
- `ARNResource` stores resource type, resource, and qualifier for parsing resource subparts.
- `std::hash<rgw::Service>` supports service maps.

## Control Flow
The header provides inline formatting operators and constructors but leaves parsing/matching implementation to the `.cc`.

## State and Persistence
No direct persistence. ARN strings are typically serialized in IAM/policy metadata elsewhere.

## Dependencies and Integration Points
Forward-declares RGW bucket/object types and uses Boost optional. It is included by account, IAM, role, and policy code.

## Risks and Edge Cases
The enum set is a compatibility boundary; missing services prevent parsing otherwise valid AWS ARNs. Constructors from strings assume callers supply resource type/path semantics correctly.

## Test Signals
Compile tests and policy tests should exercise parsing, stringification, bucket/object constructors, wildcard resource defaults, and service hashing.
