# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestWhitelistBasedResolver.java

Purpose: validates `WhitelistBasedResolver` selection of SASL properties based on fixed whitelist files, optional variable whitelist files, local address treatment, null inputs, and CIDR/IP matching.

Important APIs and types: `WhitelistBasedResolver`, `getSaslProperties`, `getDefaultProperties`, `getServerProperties`, whitelist configuration keys, `TestFileBasedIPList`, `Configuration`, `InetAddress`, and SASL privacy property maps.

Control flow: tests create fixed and variable whitelist files with exact IPs and CIDR ranges, configure resolver options, instantiate the resolver, and compare returned properties. When fixed and variable whitelists are enabled, matching IPs return default properties while nonmatching IPs return SASL privacy properties; localhost is treated as allowed. With variable whitelist disabled, only fixed whitelist and localhost are allowed. Null IP address/string inputs return privacy properties.

State and persistence: writes `fixedwhitelist.txt` and `variablewhitelist.txt` in the working directory through `TestFileBasedIPList`, then removes them. Resolver cache duration is configured but not dynamically refreshed in these tests.

Dependencies and integration points: integrates IP list file parsing, CIDR matching, Hadoop SASL/QOP configuration, and resolver configuration loading.

Risks: file cleanup is manual, so test interruption can leave files. IP string matching and local host assumptions must remain stable. The variable whitelist cache refresh path is only partially covered by configuration, not by modifying files after initialization.

Test signals: good signal for fixed/variable whitelist precedence, CIDR boundaries, localhost default allowance, disabled variable list behavior, and safe null handling.
