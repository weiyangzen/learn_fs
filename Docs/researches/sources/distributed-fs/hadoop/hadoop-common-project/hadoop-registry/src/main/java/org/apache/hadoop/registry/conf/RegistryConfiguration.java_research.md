# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/RegistryConfiguration.java

## Purpose
`RegistryConfiguration` is a thin `Configuration` subclass that imports YARN default and site resources for registry users.

## Important APIs and types
The static initializer calls `Configuration.addDefaultResource("yarn-default.xml")` and `Configuration.addDefaultResource("yarn-site.xml")`. The constructor delegates to `super()`.

## Control flow
Class loading registers the YARN resource files globally with Hadoop configuration defaults. Creating a `RegistryConfiguration` then sees registry/YARN keys from those resources.

## State and persistence behavior
No registry data is persisted. The static default-resource registration is process-level configuration state.

## Dependencies and integration points
`RegistryDNSServer.main()` and `PrivilegedRegistryDNSStarter` use this class to parse command-line and site configuration before launching DNS services. It exists because registry configuration keys historically live in YARN configuration files.

## Risks and test signals
Static default-resource registration can affect other `Configuration` instances in the same JVM. Tests should confirm expected keys load from YARN resources and isolate global configuration effects where needed.
