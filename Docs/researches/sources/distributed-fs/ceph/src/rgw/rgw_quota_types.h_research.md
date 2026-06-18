# sources/distributed-fs/ceph/src/rgw/rgw_quota_types.h

## Purpose

Defines the serialized quota data structures shared outside RGW implementation-heavy contexts. The header is intentionally dependency-light because these types are persisted and compiled in multiple Ceph components.

## Important APIs, Types, and Functions

`rgw_rounded_kb()` converts byte values to rounded-up KiB. `RGWQuotaInfo` carries `max_size`, `max_objects`, `enabled`, and `check_on_raw`. It implements versioned encode/decode, formatter dump, JSON decode, and test instance generation. `RGWQuota` groups user and bucket quota info.

## Control Flow and Data Flow

Quota config enters `RGWQuotaInfo` through JSON decode, binary decode, or default application elsewhere. Runtime enforcement reads `enabled`, negative max values as unlimited dimensions, and `check_on_raw` to choose raw-byte versus rounded-size comparison. Encoded form stores both legacy KiB size and byte-accurate `max_size` for compatibility.

## State and Persistence Behavior

`RGWQuotaInfo` is a durable encoding contract. Version 1 stores max size in KiB; version 2 adds byte-accurate `max_size`; version 3 adds `check_on_raw`. Decode preserves old data by multiplying KiB by 1024 and defaults `check_on_raw` to false for old records.

## Dependencies and Integration Points

Uses Ceph `bufferlist` encoding macros and formatter/JSON declarations without including RGW SAL or common implementation-heavy headers. Integrated with user, account, bucket metadata and quota admin APIs.

## Risks and Edge Cases

Negative `max_size` values are specially encoded by rounding the absolute value and negating, so compatibility depends on preserving sign behavior. `abs(max_size)` on the most negative `int64_t` is a theoretical overflow edge. JSON fallback from `max_size_kb` can lose byte precision. `check_on_raw` changes quota semantics for existing deployments.

## Test Signals

Round-trip encode/decode for versions 1, 2, and 3, negative unlimited values, non-KiB byte values, JSON with `max_size` and legacy `max_size_kb`, `check_on_raw` defaulting, and `RGWQuota` embedding in higher-level metadata.
