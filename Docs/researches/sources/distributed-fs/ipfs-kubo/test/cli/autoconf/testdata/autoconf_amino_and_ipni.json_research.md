# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_amino_and_ipni.json

Purpose: AutoConf fixture with both a native AminoDHT system and a delegated IPNI system. It supports tests that verify `Routing.Type=auto` treats AminoDHT as native while still delegating IPNI endpoints.

Important schema fields: `AutoConfVersion` `2025072901`, `AutoConfSchema` `1`, `AutoConfTTL` `86400`, `SystemRegistry`, `DNSResolvers`, and `DelegatedEndpoints`. `AminoDHT` includes a native bootstrap peer and delegated read/write capability declarations. `IPNI` declares provider-read delegated capability. `DNSResolvers` maps `eth.` to `https://dns.eth.limo/dns-query`.

Control flow is data-only: tests load the JSON, serve it over `httptest`, and expand `Routing.DelegatedRouters` or `Ipns.DelegatedPublishers`. State represented is external AutoConf service data, not repo persistence. Dependencies are the boxo AutoConf schema and Kubo filtering code. Risks include fixture drift from real defaults and the use of example endpoints that should not be contacted as real services. Test signal: expanded routers should include `https://cid.contact/routing/v1/providers` for IPNI and should not delegate AminoDHT URLs in auto-routing mode.
