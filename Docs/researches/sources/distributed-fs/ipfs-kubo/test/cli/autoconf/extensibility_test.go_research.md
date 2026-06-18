# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/extensibility_test.go

Purpose: integration/regression test proving AutoConf can describe previously unknown routing systems and Kubo can use their delegated endpoints without hard-coding every system name.

Important test: `TestAutoConfExtensibility_NewSystem`. It is skipped in short mode. The test builds AutoConf JSON containing `AminoDHT`, `IPNI`, and `NewSystem`, with native bootstrap data and delegated endpoint data. It uses two `httptest` servers: one for AutoConf and one for the NewSystem routing endpoint.

Control flow configures a node with `AutoConf.URL`, `AutoConf.Enabled`, short refresh interval, `Routing.Type=auto`, `Bootstrap=["auto"]`, and `Routing.DelegatedRouters=["auto"]`. After daemon startup and a wait, `bootstrap list --expand-auto` must include AminoDHT bootstrap peers, while `config Routing.DelegatedRouters --expand-auto` must include IPNI and NewSystem provider URLs with `/routing/v1/providers`. State is daemon cache and expanded routing output. Dependencies include `config.Config` mutation, slices/string matching, and live HTTP servers. Risks include timing wait, endpoint exactness, and duplicated initial mock-server setup. Test signal validates extensibility and native/delegated filtering boundaries.
