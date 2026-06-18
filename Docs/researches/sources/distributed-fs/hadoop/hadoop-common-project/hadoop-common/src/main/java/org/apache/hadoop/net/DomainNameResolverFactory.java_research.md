<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java

## Purpose
`DomainNameResolverFactory` creates `DomainNameResolver` instances from Hadoop configuration, supporting default and host-specific resolver classes.

## Important APIs and Types
The factory is private/evolving and non-instantiable. Overloads of `newInstance` accept `(Configuration, URI, configKey)`, `(Configuration, host, configKey)`, or `(Configuration, configKey)`.

## Control Flow
The URI overload extracts the URI host and appends it to the config key. The host overload builds `configKey.host`. The core overload reads a class from configuration with `DNSDomainNameResolver` as default and `DomainNameResolver` as the required interface, then instantiates it through `ReflectionUtils`.

## State and Persistence
The factory is stateless. Resolver instances may hold their own state depending on implementation.

## Dependencies and Integration Points
HA and service discovery code use this to plug in custom domain resolvers per nameservice or YARN service. It depends on Hadoop `Configuration` and reflection utilities.

## Risks and Test Signals
Host-specific configuration depends on exact host strings from URIs. Misconfigured classes fail at instantiation time. Tests should cover default resolver creation, host-suffixed key lookup, URI host extraction, custom resolver class loading, and invalid class/interface handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java -->
