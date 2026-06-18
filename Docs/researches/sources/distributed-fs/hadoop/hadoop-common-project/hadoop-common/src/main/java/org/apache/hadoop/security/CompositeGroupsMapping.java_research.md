# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CompositeGroupsMapping.java


Purpose: `CompositeGroupsMapping` composes multiple `GroupMappingServiceProvider` implementations so Hadoop can combine LDAP, shell, JNI, or custom providers without writing a new provider class.

Important APIs and types: It implements `GroupMappingServiceProvider` and `Configurable`. Configuration keys include `hadoop.security.group.mapping.providers`, `.providers.combined`, and `.provider.<name>`. `getGroups()` returns a sorted list via `TreeSet`; `getGroupsSet()` returns a `HashSet`.

Control flow: `setConf()` stores the configuration, reads whether providers are combined, and loads named provider classes. `prepareConf()` rewrites provider-scoped keys such as `.provider.foo.ldap.url` back to normal provider keys before instantiating each provider with `ReflectionUtils`. Lookup iterates providers in order, logs and skips provider exceptions, adds non-empty results, and either stops at the first hit or continues based on `combined`.

State and persistence: Provider instances and the `combined` flag are in-memory. No cache is implemented here; cache refresh/add calls are no-ops, leaving caching to outer `Groups` or inner providers.

Dependencies and integration: It integrates with `Groups` as a configurable mapping provider. It uses Hadoop `Configuration`, `ReflectionUtils`, SLF4J, and any provider classes specified in configuration.

Risks and test signals: Risks include silently missing providers when classes are not configured, result ordering differences between list and set paths, and provider-specific config rewrite mistakes. Tests should cover combined versus first-hit behavior, exception isolation, and scoped configuration translation.
