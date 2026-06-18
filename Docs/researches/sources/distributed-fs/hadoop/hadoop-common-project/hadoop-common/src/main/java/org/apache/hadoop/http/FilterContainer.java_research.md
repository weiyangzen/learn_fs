<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java

Purpose: small extension interface for objects that can accept servlet filters. It lets Hadoop filter initializers configure `HttpServer2` without depending on Jetty implementation details.

Important APIs, types, and functions: `addFilter(name, classname, parameters)` installs a filter on user-facing/default filtered contexts. `addGlobalFilter(name, classname, parameters)` installs a filter across all contexts.

Control flow: `FilterInitializer` implementations receive a `FilterContainer` during server initialization and call one of these methods to add authentication, static-user, proxy-user, or custom filters.

State and persistence: no state. Implementations decide how filter definitions and mappings are stored.

Dependencies and integration points: used by `HttpServer2`, security filter initializers, and HTTP libraries that need pluggable servlet filters.

Risks and test signals: the interface does not specify path mappings or ordering, so behavior depends on `HttpServer2`'s implementation. Tests should verify initializer ordering, parameter propagation, and the distinction between filtered and global contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/FilterContainer.java -->
