# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckConsistencyContext.java

## Purpose
`CheckConsistencyContext` wraps `CheckConsistencyPOptions` for namespace-versus-UFS consistency checks and provides default option merging.

## Important APIs, types, and functions
It extends `OperationContext<CheckConsistencyPOptions.Builder, CheckConsistencyContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. `toString()` renders the built proto options.

## Control flow
Client RPCs pass request options through `create`; internal calls can use defaults or merge user options over `FileSystemOptionsUtils.checkConsistencyDefaults(Configuration.global())`.

## State and persistence behavior
The context is per-operation mutable option state. The consistency check reads Alluxio and UFS metadata and returns inconsistent paths; this context does not persist state.

## Dependencies and integration points
It depends on configuration, consistency option protos, file-system option utilities, and `OperationContext`. It is passed to `FileSystemMaster.checkConsistency`.

## Risks
Default drift changes consistency-check behavior globally. Builder-backed options should not be shared across threads. The file contains a minor formatting inconsistency in `toString`, but no behavioral issue.

## Test signals
Tests should verify default merging and check-consistency behavior for recursive or option-dependent scans. Handler tests should confirm request option propagation.
