# Research: sources/distributed-fs/ipfs-kubo/config/dns.go

Purpose: Defines custom DNS resolver configuration for Kubo.

Important APIs/types/functions: `DNS` has `Resolvers map[string]string` and `MaxCacheTTL *OptionalDuration`.

Control flow, state, and persistence: No functions here. Resolvers map FQDN suffixes such as `"."` or `"eth."` to resolver URLs, including DoH endpoints. AutoConf expansion in `autoconf.go` can replace `"auto"` resolver values.

Dependencies and integration points: Used by DNSLink/IPNS resolution, AutoTLS DNS behavior, and config profiles. Defaults are initialized with `"." : "auto"`.

Risks and test signals: Resolver URL validation is downstream. Random AutoConf resolver selection can change effective values between calls. Tests in `autoconf_test.go` and `config_test.go` indirectly cover default resolver presence and reflection.
