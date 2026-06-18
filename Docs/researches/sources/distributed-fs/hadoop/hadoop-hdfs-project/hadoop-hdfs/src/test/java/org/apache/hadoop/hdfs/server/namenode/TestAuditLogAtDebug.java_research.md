# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuditLogAtDebug.java

## Purpose

`TestAuditLogAtDebug` verifies that the default HDFS NameNode audit logger can suppress configured commands at INFO level and emit them only when the audit logger is at DEBUG. It targets `DFS_NAMENODE_AUDIT_LOG_DEBUG_CMDLIST` handling in `DefaultAuditLogger`/`FSNamesystemAuditLogger`.

## Important APIs, Types, and Functions

The class uses `FSNamesystem.FSNamesystemAuditLogger`, `DefaultAuditLogger.initialize`, `HdfsAuditLogger.logAuditEvent`, `GenericTestUtils.setLogLevel`, SLF4J `Level`, and Mockito `spy`/`verify`. `makeSpyLogger` builds an `HdfsConfiguration`, optionally sets the comma-separated debug command list, initializes the logger, sets `FSNamesystem.AUDIT_LOG` level, and returns a spy. `logDummyCommandToAuditLog` sends a minimal audit event with loopback address and no file status.

## Control Flow

Each test constructs a spy logger at INFO or DEBUG and sends one or two dummy commands. Commands listed in the debug command list should not call `logAuditMessage` when the audit log is at INFO, but should call it at DEBUG. Commands not listed remain normal INFO audit messages. With no configured debug command list, both dummy commands log at INFO.

## State and Persistence Behavior

State is limited to the in-memory logger configuration and the global audit logger log level. No filesystem or edit-log persistence is exercised. The debug command list is parsed from configuration during `initialize`, so tests validate initialization-time state rather than live reconfiguration.

## Dependencies and Integration Points

The file depends on HDFS configuration keys, `HdfsConfiguration`, the NameNode audit logger, Java `Inet4Address`, Guava `Joiner`, JUnit 5 timeout/tests, and Mockito. It integrates with the same `FSNamesystem.AUDIT_LOG` category used by production NameNode auditing.

## Risks and Edge Cases

Because the test changes a shared logger level, ordering with other audit-log tests can matter if tests run in the same JVM without reset. The command matching is direct string matching; whitespace, case, and command-name normalization are not covered. It only verifies the final call/no-call decision to `logAuditMessage`, not the exact rendered message.

## Test Signals

The key signals are `never()` for configured debug commands at INFO, `times(1)`/`times(2)` for configured debug commands at DEBUG, logging of non-debug commands at INFO, handling of multiple configured commands, and behavior when no command list is configured.
