# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/LdapGroupsMapping.java


Purpose: `LdapGroupsMapping` implements `GroupMappingServiceProvider` by querying LDAP directories for user group membership, including Active Directory `memberOf`, generic group membership filters, POSIX group semantics, nested group traversal, failover URLs, bind-user rotation, and SSL stores.

Important APIs and types: It is configurable through many `hadoop.security.group.mapping.ldap.*` keys for URLs, SSL, keystore/truststore, bind users/passwords/aliases/files, base DNs, user/group filters, member attributes, POSIX attributes, hierarchy depth, timeouts, attempts, and context factory. Public methods include synchronized `getGroups()`, `getGroupsSet()`, `setConf()`, `getConf()`, `getLdapUrls()`, no-op cache methods, and nested `LdapSslSocketFactory`.

Control flow: `setConf()` validates URLs, cycles LDAP URLs, loads SSL and bind-user config, derives user and group base DNs, selects one-query mode when `memberOf` is set, configures POSIX/custom filter state, sets `SearchControls`, selects a JNDI context factory, and stores retry/failover counts. `getGroupsSet()` retries up to `numAttempts`, rotating bind users on `AuthenticationException`, failing over LDAP URLs after configured attempts, clearing `ctx` after failures, and returning empty set after all attempts. `doGetGroups()` obtains a `DirContext`, searches for the user, optionally extracts groups from `memberOf`, otherwise does a second group search, and optionally walks parent groups recursively.

State and persistence: Runtime state includes a cached `DirContext`, current LDAP URL, bind-user iterator/current bind user, SSL store paths/passwords, filters, attributes, and retry settings. The context is intentionally used under synchronized access because the underlying LDAP context is not thread-safe. Passwords can be read from credential providers, config, or files; no state is persisted.

Dependencies and integration: It depends on JNDI LDAP classes, SSL key/trust manager APIs, Hadoop `Configuration`, credential providers, and `Groups` for outer caching. `LdapSslSocketFactory` uses static configuration because JNDI creates socket factories by class name.

Risks and test signals: Tests should cover one-query fallback, POSIX lookup, custom group filter args, nested group traversal, empty user search, LDAP URL failover, bind-user rotation, password source precedence, SSL factory setup, context-classloader workaround, and search timeout attributes. Risks include static SSL factory state, broad synchronized lookup latency, sensitive password handling, and filter injection/misconfiguration through custom LDAP filters.
