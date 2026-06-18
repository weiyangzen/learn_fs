# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolUtils.java

## Purpose

`ReconfigurationProtocolUtils.java` contains shared client-side conversion logic for reconfiguration status responses. It turns `GetReconfigurationStatusResponseProto` into the common `ReconfigurationTaskStatus` model.

## Important APIs, Types, and Functions

The class is `final` with a private constructor. Its single public method, `getReconfigurationStatus(GetReconfigurationStatusResponseProto response)`, extracts start/end time and converts each `GetReconfigurationStatusConfigChangeProto` into a `ReconfigurationUtil.PropertyChange` mapped to an optional error message.

## Control Flow

The method initializes `statusMap` to `null`, always reads `startTime`, sets `endTime` only when present, and creates a Guava hash map only if the response contains changes. For each change, it builds a `PropertyChange(name, newValue, oldValue)`, reads `errorMessage` only when present, stores `Optional.ofNullable(errorMessage)`, and returns a `ReconfigurationTaskStatus`.

## State and Persistence Behavior

No state is stored. The returned task status is a snapshot of remote reconfiguration state at response time. A `null` status map means there were no change entries.

## Dependencies and Integration Points

Dependencies are Hadoop `ReconfigurationTaskStatus`, `PropertyChange`, generated reconfiguration protos, Java `Optional`, and shaded Guava `Maps`. It is used by `ReconfigurationProtocolTranslatorPB` and any client-side code needing the same conversion.

## Risks and Edge Cases

The distinction between `null` status map and an empty map is part of the status contract and may matter to callers. Missing end time is normalized to `0`, representing an in-progress task. Duplicate property changes would overwrite earlier entries because the map key is `PropertyChange`.

## Test Signals

Tests should cover in-progress responses without end time, completed responses with end time, empty changes, changes with and without error messages, and duplicate property-change behavior if that is a supported server case.
