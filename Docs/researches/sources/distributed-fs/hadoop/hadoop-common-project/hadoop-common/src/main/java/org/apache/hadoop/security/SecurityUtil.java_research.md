# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SecurityUtil.java

Purpose: central security utility class for Kerberos principal expansion, token service naming, DNS resolution, RPC security metadata discovery, privileged execution, authentication configuration, ZooKeeper auth parsing, and ZooKeeper SSL client setup.

Important APIs/types/functions: `setConfiguration` configures token service IP/hostname mode, DNS cache expiry, slow lookup logging, and `DomainNameResolver`. `getServerPrincipal` replaces `_HOST` in service principals. `login` resolves configured keytab/principal and delegates to `UserGroupInformation.loginUserFromKeytab`. `buildTokenService`, `setTokenService`, and `getTokenServiceAddr` define token service identities. `getKerberosInfo`, `getClientPrincipal`, and `getTokenInfo` query `SecurityInfo` providers. `doAsLoginUser`, `doAsCurrentUser`, and `doAsLoginUserOrFatal` wrap UGI `doAs`. `getZKAuthInfos`, `validateSslConfiguration`, `setSslConfiguration`, and `TruststoreKeystore` integrate ZooKeeper auth and TLS.

Control flow: static initialization calls `setConfigurationInternal(new Configuration())`. Changing token service mode swaps between `StandardHostResolver` and `QualifiedHostResolver`. Qualified resolution handles IP literals, rooted FQDNs, dotted hostnames, search domains, and loopback without unnecessary reverse lookups. SSL configuration validates four required fields before setting ZooKeeper secure client properties.

State/persistence: static resolver mode, host resolver, DNS resolver, logging thresholds, cache interval, ServiceLoader, and test provider array. No durable writes. Host resolver may own a Guava cache.

Dependencies/integration: `UserGroupInformation`, `HadoopKerberosName`, `NetUtils`, `DNS`, `DomainNameResolverFactory`, `SecurityInfo`, `Token`, `ZKUtil`, ZooKeeper `ZKClientConfig`, DNSJava resolver config, and Hadoop common configuration keys.

Risks: global static configuration affects all callers in-JVM; token service identity changes can break token matching; hostname canonicalization and DNS search behavior are security-sensitive; `doAsLoginUserOrFatal` exits JVM on failure; SSL passwords are read as plain strings in config object. Test signals include `_HOST` substitution, null/0.0.0.0 host behavior, IP-vs-host token services, resolver cache error propagation, provider priority, invalid auth method config, ZK auth indirection, and missing SSL fields.
