# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/LookupTask.java

## Purpose
`LookupTask` wraps an xbill DNS lookup in a `Callable<Record[]>` so remote lookup can run with a timeout.

## Important APIs and types
The constructor stores a `Name` and integer DNS `type`. `call()` returns `new Lookup(name, type).run()`.

## Control flow
`RegistryDNS.getRecords()` creates a single-thread executor, submits `LookupTask`, and waits up to 1500 ms. This isolates potentially blocking upstream DNS calls from the main response path.

## State and persistence behavior
The task is stateless after construction and does not persist data. It reads from globally configured xbill DNS resolver state.

## Dependencies and integration points
It depends on xbill `Lookup`, `Name`, and `Record`, and is only used by `RegistryDNS` remote lookup fallback.

## Risks and test signals
Since `Lookup` uses global resolver configuration, tests should set resolver state deterministically. Timeout and exception behavior are controlled by `RegistryDNS.getRecords()`, not this class. Tests should verify that upstream lookup failures return null/empty responses without blocking DNS serving threads indefinitely.
