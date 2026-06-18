# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyUsers.java

Purpose: comprehensive coverage for proxy-user impersonation authorization: group/user allow rules, host allow rules, wildcards, CIDR ranges, null arguments, duplicate normalization, provider override, custom configuration prefixes, missing hosts, optional netgroups, and a manual load-test harness.

Important APIs and types: `ProxyUsers`, `DefaultImpersonationProvider`, `ImpersonationProvider`, `AuthorizationException`, `UserGroupInformation`, `Groups`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_IMPERSONATION_PROVIDER_CLASS`, `StringUtils`, `InetAddress`, and `NativeCodeLoader`.

Control flow: standard tests build configurations using provider helper keys, refresh global proxy settings, construct real/proxy UGIs, then assert both string-host and `InetAddress` authorization paths. Cases cover allowed group from good IP, disallowed IP, disallowed group, explicit user lists, wildcard groups/users/IPs, IP ranges, null UGI/address exceptions, deduped group and host entries, custom provider class that allows only real users in `sudo_<proxied>` groups, values with spaces, null/empty/custom prefixes, and no-hosts denial. Optional netgroup test runs only with native code and configured netgroup mapping. Static `loadTest` and `main` provide manual performance probing for large IP/range lists.

State and persistence: repeatedly mutates static proxy-user configuration and default impersonation provider state. No durable files are written. Optional netgroup path depends on host config and native libraries.

Dependencies and integration points: integrates UGI proxy identity, group mapping, machine/IP list matching, CIDR parsing, provider pluggability, and both hostname string and address overloads.

Risks: global static proxy config can create order dependency if tests run concurrently. Manual netgroup and load-test paths are environment-dependent and not normal automated checks. Fake `InetAddress` construction uses synthetic hostnames from IP strings to test address overloads while preserving address bytes.

Test signals: strong signal for impersonation authorization matrix, dedupe behavior, custom prefixes/providers, input validation, and address matching.
