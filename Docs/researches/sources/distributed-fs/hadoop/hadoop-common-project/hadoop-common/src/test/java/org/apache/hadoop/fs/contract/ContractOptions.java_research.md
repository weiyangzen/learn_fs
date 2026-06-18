# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractOptions.java

## Purpose
`ContractOptions` centralizes configuration keys used by filesystem contract tests. It defines feature flags, limits, behavioral quirks, and test tuning options so contract XML resources and test classes use stable names.

## Important APIs, Types, And Functions
This is an interface of constants, not an executable API. Important groups include creation behavior (`CREATE_OVERWRITES_DIRECTORY`, delayed visibility, file-under-file), namespace behavior (`IS_CASE_SENSITIVE`, `IS_BLOBSTORE`), rename semantics, capability flags for append, setTimes, seek, positioned reads, file references, content checks, hflush/hsync, vectored IO behavior, block locality, concat, root-test permission, max path/file sizes, and random seek count.

## Control Flow
There is no runtime control flow. `AbstractFSContract` implementations combine `FS_CONTRACT_KEY`, filesystem scheme, and these option names to load boolean or scalar capabilities from XML resources and configuration overlays.

## State And Persistence
The file has no mutable state. Its constants shape persisted test configuration in XML and runtime `Configuration` objects.

## Dependencies And Integration Points
Every contract class and many abstract contract suites depend on these keys to decide whether to run, skip, or alter expectations. Local and raw local contracts adjust some keys at runtime based on host platform.

## Risks
Renaming or changing key spelling breaks existing contract XML resources. Wrong defaults can either hide filesystem bugs by skipping tests or cause false failures where a backend deliberately lacks a feature.

## Test Signals
Signals are contract-loaded tests finding expected keys, feature-gated tests skipping only when intended, and XML resources using the same constant names.
