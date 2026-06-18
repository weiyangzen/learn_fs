# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketOptions.java

## Purpose
`ListBucketOptions` is a mutable options object for S3 list-object operations. It supports both ListObjects v1 and ListObjectsV2 request parameters.

## Important APIs, Types, and Functions
Defaults are `DEFAULT_MAX_KEYS = 1000` and `DEFAULT_ENCODING_TYPE = "url"`. Fields include marker, prefix, max keys, delimiter, encoding type, list type, continuation token, and start-after. The class provides `defaults`, getters, fluent setters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, and Persistence
`defaults` returns a new private-constructor instance with prefix `""`, max keys `1000`, delimiter and encoding null, marker null, list type null, continuation token null, and start-after null. Setters mutate and return `this`. There is no validation here; validation occurs in consumers such as `ListBucketResult`.

## Dependencies and Integration Points
It is consumed by S3 bucket-list response construction and likely request parsing. Guava `Objects` and `MoreObjects` provide equality and string formatting.

## Risks
The object is mutable and not thread-safe. It does not reject negative `maxKeys` or unsupported `listType`, leaving callers to validate. Default `encodingType` is null despite the constant, so callers must explicitly set URL encoding when desired.

## Test Signals
Signals include default values, fluent setter chaining, equality/hash behavior, and integration with `ListBucketResult` for v1/v2 marker and continuation-token behavior.
