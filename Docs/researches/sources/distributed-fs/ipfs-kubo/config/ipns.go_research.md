# Research: sources/distributed-fs/ipfs-kubo/config/ipns.go

Purpose: Defines IPNS publishing/resolution configuration.

Important APIs/types/functions: `DefaultIpnsMaxCacheTTL`; `Ipns` fields include republish period, record lifetime, resolve cache size, max cache TTL, pubsub usage flag, and delegated publisher URLs.

Control flow, state, and persistence: No functions. Values are persisted in config and consumed by namesys/IPNS services. Delegated publishers can contain `"auto"` and are expanded in `autoconf.go`.

Dependencies and integration points: Uses `math` and `time` for maximum default TTL. Init defaults set resolve cache size and delegated publishers.

Risks and test signals: Republish period/lifetime are strings, so validation happens downstream. Delegated publisher auto expansion depends on AutoConf and routing type. Tests in `autoconf_test.go` cover init/profile placeholder behavior.
