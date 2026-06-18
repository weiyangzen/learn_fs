<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java

## Purpose
Provides assertion helpers for Hadoop service lifecycle tests, covering expected service states, `BreakableService` state-count checks, and configuration-key presence.

## Important APIs, Types, And Functions
Extends JUnit `Assertions` and exposes `assertServiceStateCreated`, `assertServiceStateInited`, `assertServiceStateStarted`, `assertServiceStateStopped`, `assertServiceInState`, `assertStateCount`, and `assertServiceConfigurationContains`.

## Control Flow
State helpers delegate to `assertServiceInState`, which compares `service.getServiceState()` to the expected enum and includes the service name in failures. `assertStateCount` compares a `BreakableService` count for a given state. Configuration assertion checks that `service.getConfig().get(key)` is non-null.

## State And Persistence
No state is stored; this is a static assertion utility.

## Dependencies And Integration Points
Depends on Hadoop `Service`, `BreakableService`, and JUnit assertions. It supports the service package's test suite by centralizing common lifecycle assertions.

## Risks
Assertions only check high-level state and configuration presence, not deeper lifecycle side effects. Extending `Assertions` is convenient but not necessary and can make static imports ambiguous.

## Test Signals
Failure messages identify the service name, expected/actual state, count mismatches, and missing configuration keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/ServiceAssert.java -->
