# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/PathCapabilitiesSupport.java

## Purpose
Shared validation/normalization helper for PathCapabilities.hasPathCapability arguments.

## Important APIs, Types, and Functions
validatePathCapabilityArgs(Path,String).

## Control Flow
Checks path and capability are non-null and capability non-empty, then lowercases capability with Locale.ENGLISH for switch-friendly matching.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by AbstractHttpFileSystem and other PathCapabilities implementations.

## Risks and Test Signals
Tests should cover null/empty inputs, locale-stable lowercasing, and capability switch matching.
