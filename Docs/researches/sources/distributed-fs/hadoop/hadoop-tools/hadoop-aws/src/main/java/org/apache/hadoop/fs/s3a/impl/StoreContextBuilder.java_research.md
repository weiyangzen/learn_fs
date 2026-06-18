# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextBuilder.java

## Purpose
`StoreContextBuilder` assembles the inputs needed to create a `StoreContext`.

## Important APIs and Types
It has setters for filesystem URI, bucket, configuration, username, owner, executor, executor capacity, invoker, statistics, storage statistics, input policy, change detection, multi-object delete flag, list-v1 flag, context accessors, auditor, CSE enablement, and performance flags. `build()` constructs `StoreContext`.

## Control Flow
Each setter assigns a field and returns the builder. Defaults are `S3AInputPolicy.Normal`, multi-object delete enabled, list-v1 disabled, and CSE disabled. `build()` passes all fields directly to the package-private `StoreContext` constructor.

## State and Persistence
The builder is mutable transient state only. It creates immutable context objects.

## Dependencies and Integration Points
It integrates `S3AFileSystem` initialization with `StoreContext` creation and depends on S3A metrics, audit, security, and performance flag types.

## Risks and Edge Cases
No validation is performed in the builder, so missing dependencies may surface later as null dereferences. Builder reuse can unintentionally carry previous settings.

## Test Signals
Tests should verify defaults, all setter propagation, CSE and performance flag handling, and behavior when optional vs required fields are omitted.
