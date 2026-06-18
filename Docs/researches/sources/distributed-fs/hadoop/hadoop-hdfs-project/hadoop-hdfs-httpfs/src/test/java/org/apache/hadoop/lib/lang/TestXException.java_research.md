# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/lang/TestXException.java

Purpose: Unit tests for `XException` formatting, error identity, and cause wrapping.

Important APIs/types/functions: enum `TestERROR` implements `XException.ERROR` with template `{0}`; test `testXException` exercises constructors with no args, formatted message arg, normal cause, and an existing `XException`.

Control flow: each constructor variant is created and checked for `getError`, message text, and cause. Wrapping an `XException` must preserve the original error and message while using the original exception as the cause.

State and persistence: no persistent state.

Dependencies/integration: depends on `HTestCase`, JUnit, and the common error-template contract used by server/service exceptions.

Risks and test signals: good signal that error codes remain stable and messages include the enum prefix. It does not cover multiple formatting parameters or null templates.
