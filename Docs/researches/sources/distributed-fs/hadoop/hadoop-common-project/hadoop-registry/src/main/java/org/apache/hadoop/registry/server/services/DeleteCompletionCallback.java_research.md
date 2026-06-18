# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/DeleteCompletionCallback.java

## Purpose
`DeleteCompletionCallback` is a Curator background callback that counts completed delete events and logs them at debug level.

## Important APIs and types
It implements `BackgroundCallback`. State is `AtomicInteger events`. `processResult(CuratorFramework, CuratorEvent)` increments the counter. `getEventCount()` returns the count.

## Control flow
When passed to a Curator delete operation, Curator invokes `processResult` asynchronously after completion, and the callback increments its event count regardless of event status.

## State and persistence behavior
Only an in-memory counter is maintained. It does not persist data or inspect delete success semantics beyond receiving an event.

## Dependencies and integration points
It depends on Curator framework/event APIs and is intended for registry admin async deletion flows.

## Risks and test signals
The counter increments for every callback event, including failures if Curator delivers them. Tests should verify callback invocation count and, where needed, pair it with event result-code assertions outside this helper.
