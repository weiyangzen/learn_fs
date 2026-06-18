# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/NetUtilsTestResolver.java

Purpose: Test DNS resolver for `SecurityUtil.QualifiedHostResolver` behavior with deterministic search domains and host mappings.

Important APIs/types/functions: `install`, `addResolvedHost`, overridden `getInetAddressByName`, exposed `getByExactName`, `getByNameWithSearch`, `getHostSearches`, and `reset`.

Control flow: `install` creates a resolver with search domains `a.b`, `b`, `c`, seeds three fully qualified hosts, and assigns it to global `SecurityUtil.hostResolver`. Resolution records every attempted host string and returns configured `InetAddress` instances or throws `UnknownHostException`.

State and persistence: mutable `resolvedHosts`, `hostSearches`, and global `SecurityUtil.hostResolver`.

Dependencies/integration points: Hadoop security token service host resolution and Java `InetAddress`.

Risks: global resolver mutation can leak between tests if not restored; host search ordering is captured as mutable state; not thread-safe.

Test signals: consumers can verify exact DNS search attempts and deterministic address results without relying on external DNS.
