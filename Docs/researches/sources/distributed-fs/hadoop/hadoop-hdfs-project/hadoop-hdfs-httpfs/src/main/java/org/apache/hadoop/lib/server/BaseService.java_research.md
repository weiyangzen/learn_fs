<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java

## Purpose
`BaseService` is a convenience superclass for `Service` implementations. It captures the owning `Server`, extracts service-specific configuration by prefix, and supplies default no-op lifecycle/dependency hooks.

## Important APIs, Types, And Functions
The constructor stores a service prefix. Final `init(Server)` records the server, builds a new `Configuration(false)`, copies all resolved server config keys under `serverPrefix.servicePrefix.`, strips that prefix, and delegates to protected abstract `init()`. Defaults for `postInit`, `destroy`, `getServiceDependencies`, and `serverStatusChange` are no-ops/empty. Helpers expose `getPrefix`, `getServer`, `getPrefixedName`, and `getServiceConfig`.

## Control Flow
`Server.initServices` calls `service.init(this)` on each service. Subclasses implement protected `init()` and use the trimmed service config rather than parsing global keys directly.

## State And Persistence
Instance state is prefix, owning server, and a trimmed service configuration snapshot. No persistent data is written.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `ConfigurationUtils.resolve`, and the `Service`/`Server` lifecycle. All concrete services in this subset extend it.

## Risks
The final `init(Server)` prevents subclasses from customizing the prefix extraction sequence. Config is copied at initialization; later server config changes are not reflected. Prefix matching is string-based, so malformed prefixes can leak or miss settings.

## Test Signals
Tests should verify prefix stripping, resolved-variable copying, default empty dependencies/status hooks, and subclass initialization seeing only trimmed service config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/server/BaseService.java -->
