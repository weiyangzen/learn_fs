<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java

## Purpose
Converts TTL action values between Alluxio gRPC wire enum `TtlAction` and journal protobuf enum `PTtlAction`.

## Important APIs, Types, And Functions
- `fromProtobuf(PTtlAction)` maps journal values to wire values.
- `toProtobuf(TtlAction)` maps wire values to journal values.
- Null inputs default to `DELETE_ALLUXIO` in both directions.

## Control Flow
Each method switches on the enum and returns the corresponding value for `DELETE_ALLUXIO`, `DELETE`, or `FREE`. Unknown enum values throw `IllegalStateException`.

## State And Persistence Behavior
The class is stateless. It influences persistence compatibility because TTL actions stored in journal protobufs must round-trip to the public wire model correctly.

## Dependencies And Integration Points
Depends on `alluxio.grpc.TtlAction` and `alluxio.proto.journal.File.PTtlAction`. It is a low-level bridge used by master metadata journaling and RPC conversion code.

## Risks And Edge Cases
New enum values require updating both switch statements. The null default preserves compatibility but can hide missing values by treating them as `DELETE_ALLUXIO`.

## Test Signals
Tests should verify each enum round-trips, null defaults are intentional, and unknown values fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/ProtobufUtils.java -->
