# sources/distributed-fs/ceph/src/rgw/rgw_public_access.h

## Purpose
`rgw_public_access.h` defines the serializable representation of S3 Public Access Block settings.

## Important APIs, Types, And Functions
`PublicAccessBlockConfiguration` has four bool fields: `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, and `RestrictPublicBuckets`. It implements Ceph buffer encode/decode version 1, declares XML decode/dump, and has a `WRITE_CLASS_ENCODER`. The header also declares `operator<<` and `config_union()`.

## Control Flow
There is no complex control flow. Encoding writes all four bools in fixed order; decoding reads the same order.

## State And Persistence
This struct is the durable attr payload for public-access block configuration. Default construction disables all restrictions.

## Dependencies And Integration Points
It depends on Ceph encoding and XML/formatter forward declarations. RGW bucket public-access operations and policy-status calculations use it.

## Risks And Test Signals
Risks include changing field order/version incorrectly, default false semantics, and mismatch between buffer and XML representations. Tests should cover default config, encode/decode, XML parse/dump, account/bucket union, and request behavior for each flag.
