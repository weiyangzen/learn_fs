# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HttpCrossOriginFilterInitializer.java


Purpose: `HttpCrossOriginFilterInitializer` conditionally installs Hadoop's CORS servlet filter on HTTP servers.

Important APIs and types: `PREFIX` is `hadoop.http.cross-origin.`, `ENABLED_SUFFIX` is `enabled`, `initFilter()` registers a global `CrossOriginFilter` when enabled, and `getFilterParameters()` strips the prefix from matching configuration entries.

Control flow and state: The initializer is stateless. On startup it checks `<prefix>enabled`; if false it logs an informational message and does nothing. If true it passes all prefixed options to the global filter.

Dependencies and integration: It depends on Hadoop `FilterContainer`, `FilterInitializer`, `CrossOriginFilter`, and `Configuration`. It integrates with web UIs and REST endpoints exposed by Hadoop services.

Risks and test signals: Tests should cover disabled behavior, prefix stripping, enabled registration, and subclass overrides of `getPrefix()` or `getEnabledConfigKey()`. Misconfigured broad origins can weaken browser-side access controls.
