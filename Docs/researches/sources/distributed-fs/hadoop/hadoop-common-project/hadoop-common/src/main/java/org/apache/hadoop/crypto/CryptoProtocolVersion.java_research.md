# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoProtocolVersion.java`

## Purpose

`CryptoProtocolVersion` models versions of the client/server protocol used for HDFS encryption features.

## Important APIs and Types

Enum constants are `UNKNOWN("Unknown",1)` and `ENCRYPTION_ZONES("Encryption zones",2)`. Methods include `supported`, `supports`, `setUnknownValue`, `getUnknownValue`, `getDescription`, `getVersion`, and `toString`.

## Control Flow

`supported` returns the static array currently containing only `ENCRYPTION_ZONES`. `supports` rejects a value with the same version as `UNKNOWN`, then scans all enum values and returns true if any enum constant has the same numeric version.

## State and Persistence

Enum constants store description, numeric version, and mutable `unknownValue`. The static `supported` array is returned directly, so callers can mutate its contents.

## Dependencies and Integration Points

The enum is used in HDFS encryption negotiation and compatibility checks. Numeric versions are wire/protocol values, while descriptions are human-readable.

## Risks

Returning the internal supported array allows accidental modification of global supported versions. `supports` scans all values, not the `supported` array, so future enum constants could be reported supported even if not added to `supported`. `getUnknownValue` can unbox null. `UNKNOWN` and real versions must keep unique numeric IDs.

## Test Signals

Tests should cover supported list contents, `supports` behavior for unknown and real versions, unknown value preservation, mutation risk of returned arrays, and compatibility when adding new protocol versions.
