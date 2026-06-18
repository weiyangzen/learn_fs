# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Tristate.java

## Purpose
`Tristate` represents true, false, and unknown values, mainly for S3A metadata where a boolean property may not be known without extra remote calls.

## Important APIs, Types, and Functions
Enum values are `TRUE`, `FALSE`, and `UNKNOWN`. APIs are `getMapping()`, `isBoolean()`, `fromBool(boolean)`, and `from(Optional<Boolean>)`.

## Control Flow and State
Each enum value stores an `Optional<Boolean>`. Conversion from boolean maps directly; conversion from optional maps empty to `UNKNOWN`.

## State and Persistence Behavior
State is static enum data only. The optional mapping is immutable by convention.

## Dependencies and Integration Points
Dependencies are Java `Optional`. S3A file status classes use it for empty-directory knowledge and conversions between S3 status and located status.

## Risks and Test Signals
Risks are low, but code comments warn logic assumes exactly three values. Tests should cover optional mapping, boolean detection, conversions, and status classes preserving `UNKNOWN` distinctly from false.
