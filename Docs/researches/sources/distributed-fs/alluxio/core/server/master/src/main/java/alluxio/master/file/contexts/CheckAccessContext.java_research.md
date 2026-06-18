# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CheckAccessContext.java

## Purpose
`CheckAccessContext` wraps `CheckAccessPOptions` for file-system master access-check operations and provides master default merging.

## Important APIs, types, and functions
It extends `OperationContext<CheckAccessPOptions.Builder, CheckAccessContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. `toString()` includes built proto options.

## Control flow
RPC handlers usually call `create` from request options. Internal callers can use `mergeFrom` or `defaults` to combine caller options with `FileSystemOptionsUtils.checkAccessDefaults(Configuration.global())`.

## State and persistence behavior
The context stores mutable protobuf option builder state plus inherited operation metadata/call trackers. It does not mutate persistent metadata; it controls how `checkAccess` runs.

## Dependencies and integration points
It depends on global configuration, `CheckAccessPOptions`, `FileSystemOptionsUtils`, and `OperationContext`. It is passed to `FileSystemMaster.checkAccess`.

## Risks
Misusing `create` versus `mergeFrom` can skip master defaults. Since options are builder-backed, callers can mutate options after context creation if they retain references.

## Test signals
Context tests should assert default merging, `toString`, and operation metadata inheritance. RPC handler tests should verify correct context construction.
