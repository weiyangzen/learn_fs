# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSRESTConstants.java

## Purpose
`KMSRESTConstants` defines shared REST resource, query-parameter, JSON-field, and error-field names for Hadoop KMS client/server communication.

## Important APIs and types
Constants include service version `/v1`, resources such as `key`, `keys`, `keyversion`, subresources like `_metadata`, `_versions`, `_eek`, `_currentversion`, `_invalidatecache`, and `_reencryptbatch`, EEK operations `generate`, `decrypt`, `reencrypt`, JSON fields such as `iv`, `name`, `cipher`, `length`, `material`, `versionName`, and error fields `exception` and `message`.

## Control flow
There are no methods. Client and server code compose URLs and JSON payloads from these constants.

## State and persistence
No state is stored. Constants are API compatibility surface for wire-format persistence in clients and servers.

## Dependencies and integration points
It depends only on Hadoop interface annotations. `KMSClientProvider`, KMS server handlers, and `KMSUtil` JSON conversion code must agree on these values.

## Risks
Any rename is a wire incompatibility. Because constants are simple strings, tests must catch endpoint drift between client and server.

## Test signals
Tests should exercise KMS client/server round trips rather than this class alone, ensuring all constants match accepted REST paths and JSON payloads.
