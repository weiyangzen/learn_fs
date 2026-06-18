# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJetty.java

## Purpose
Marker annotation for test methods that need an embedded Jetty server.

## Important APIs, Types, And Functions
`@interface TestJetty` has runtime retention and method target. It has no members; marker presence activates `TestJettyHelper`.

## Control Flow
The annotation has no control flow. `TestJettyHelper.beforeEach` detects it via reflection and creates a server that tests can configure and start.

## State, Persistence, And Dependencies
No state is stored in the annotation. Runtime visibility is required for JUnit extension code.

## Integration Points
Used by `HTestCase`-style tests with `TestJettyHelper.getJettyServer()`, `getJettyURL()`, and `getAuthority()`.

## Risks
Because it carries no configuration, SSL mode or keystore selection must come from the helper instance rather than the annotation. Forgetting the annotation makes helper accessors throw `IllegalStateException`.

## Test Signals
Tests annotated with `@TestJetty` should receive a bindable Jetty server; unannotated tests should not.
