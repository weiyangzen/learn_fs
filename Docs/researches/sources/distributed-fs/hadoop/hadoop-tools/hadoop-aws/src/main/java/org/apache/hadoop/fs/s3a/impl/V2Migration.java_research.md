# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/V2Migration.java

## Purpose
`V2Migration` retains SDK v1 migration diagnostics after S3A's move to AWS SDK v2.

## Important APIs and Types
It exposes `SDK_V2_UPGRADE_LOG` and `v1RequestHandlersUsed(String handlers)`, which logs ignored v1 request handler configuration through `LogExactlyOnce`.

## Control Flow
When legacy v1 request handlers are encountered, callers invoke `v1RequestHandlersUsed()`. The warning is emitted once on the SDK v2 upgrade logger.

## State and Persistence
The class is stateless except for logger and `LogExactlyOnce` suppression state. It does not persist or alter configuration.

## Dependencies and Integration Points
It depends on S3A audit constants, internal upgrade log name, SLF4J, and Hadoop `LogExactlyOnce`. It integrates with configuration migration/compatibility checks.

## Risks and Edge Cases
The method says handlers are ignored; users relying on v1 request handlers may lose behavior silently after the one-time warning. Logging level/wording matters for migration diagnostics.

## Test Signals
Tests should verify one-time logging behavior and invocation when legacy audit request handler settings are present.
