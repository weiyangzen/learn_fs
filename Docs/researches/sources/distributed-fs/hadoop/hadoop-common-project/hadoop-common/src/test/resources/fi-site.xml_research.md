# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/fi-site.xml

## Purpose
`fi-site.xml` is a fault-injection test configuration. It sets a wildcard probability for fault injection controls used by Hadoop tests.

## Important Properties
The single property `fi.*=0.00` effectively disables all wildcard fault-injection events unless a test overrides a narrower key.

## Control Flow
Fault-injection-aware test code reads matching `fi.*` keys from `Configuration` and decides whether to trigger injected failures. With `0.00`, default control flow remains non-faulting.

## State And Persistence
The file persists only the default injection probability. It creates no state and does not record injection events.

## Dependencies And Integration Points
It integrates with Hadoop's fault-injection utilities and tests that intentionally override or consume `fi.*` properties.

## Risks
If the default is raised, unrelated tests can become nondeterministic. If the file is not loaded where expected, tests that rely on a known no-fault baseline can become environment-dependent.

## Test Signals
Fault-injection tests should show deterministic non-injected behavior by default, with explicit overrides enabling failure paths in targeted tests.
