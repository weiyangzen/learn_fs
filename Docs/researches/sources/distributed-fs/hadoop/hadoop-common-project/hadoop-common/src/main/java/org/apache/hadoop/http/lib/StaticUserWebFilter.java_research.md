<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java

Purpose: filter initializer that supplies a static remote user for web UIs when no authenticated user exists, making secure-cluster web pages usable without full HTTP authentication.

Important APIs, types, and functions: nested `User` implements `Principal` with name-based equality. Nested `StaticUserFilter` wraps unauthenticated `HttpServletRequest`s so `getUserPrincipal()` and `getRemoteUser()` return the configured static user. `initFilter()` registers the filter with the container. `getUsernameFromConf()` reads `hadoop.http.staticuser.user` or deprecated `dfs.web.ugi`.

Control flow: during `HttpServer2` filter initialization, this initializer adds `static_user_filter`. At request time the filter preserves existing authenticated users and only wraps anonymous requests.

State and persistence: filter instance stores immutable username/principal after init. No persistence.

Dependencies and integration points: integrates Hadoop configuration keys, `FilterContainer`, `FilterInitializer`, servlet filters, and downstream admin ACL checks that rely on remote user.

Risks and test signals: static users can grant UI identity in deployments without authentication, so configuration must align with ACL expectations. Deprecated `dfs.web.ugi` parsing uses the first comma-separated field. Tests should cover default user, deprecated key warning/path, preservation of authenticated users, wrapper principal behavior, and ACL interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/lib/StaticUserWebFilter.java -->
