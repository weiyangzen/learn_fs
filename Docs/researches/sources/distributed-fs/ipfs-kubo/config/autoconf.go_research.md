# Research: sources/distributed-fs/ipfs-kubo/config/autoconf.go

Purpose: Defines AutoConf configuration and runtime expansion of `"auto"` placeholders for bootstrap peers, DNS resolvers, delegated routers, and delegated IPNS publishers.

Important APIs/types/functions: `AutoConf`, constants including `AutoPlaceholder`, `DefaultAutoConfURL`, and refresh/cache defaults. Helpers include `getNativeSystems`, `selectRandomResolver`, `expandAutoConfSlice`, `getAutoConf`, `DNSResolversWithAutoConf`, `BootstrapWithAutoConf`, `BootstrapPeersWithAutoConf`, `DelegatedRoutersWithAutoConf`, `DelegatedPublishersWithAutoConf`, `ExpandAutoConfValues`, and `ExpandConfigField`.

Control flow, state, and persistence: Runtime expansion is lazy and reads cached autoconf data only; it avoids network I/O during config access by using `client.GetCached()`. DNS expansion replaces configured `"auto"` values when matching autoconf data exists, preserves custom resolvers, and adds autoconf defaults for missing domains. Bootstrap expansion inserts autoconf peers once for each placeholder group. Delegated endpoint expansion delegates path filtering to Boxo autoconf. `ExpandAutoConfValues` clones only the top-level map before replacing supported fields, so nested maps are mutated when present.

Dependencies and integration points: Integrates `github.com/ipfs/boxo/autoconf`, Kubo `Config`, routing type, bootstrap parsing, and config-display paths. The daemon and config commands need these methods to agree on runtime expansion.

Risks and test signals: Random DNS resolver selection can make outputs non-deterministic. The shallow `maps.Clone` may surprise callers expecting a deep copy. Singleton client state in `autoconf_client.go` can make test/config changes sticky. `autoconf_test.go` covers defaults, profile wiring, and init placeholders but not expansion with real cached autoconf.
