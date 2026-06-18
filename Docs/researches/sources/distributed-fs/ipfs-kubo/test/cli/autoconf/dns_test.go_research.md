# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/dns_test.go

Purpose: tests AutoConf-provided DNS-over-HTTPS resolver integration for IPNS/DNSLink resolution. It verifies that `DNS.Resolvers` entries set to `auto` remain visible in config but resolve through endpoints supplied by AutoConf.

Important types and functions: `mockDoHServer`, `newMockDoHServer`, `handleDNSQuery`, `getRequests`, `testDNSResolutionWithAutoDoH`, and `testDNSErrorHandling`. The mock server accepts DoH GET `?dns=` and POST wire-format requests, unpacks `miekg/dns` messages, records query names, and returns TXT DNSLink answers or NXDOMAIN depending on `responseFunc`.

Control flow builds an AutoConf JSON whose `DNSResolvers` maps a suffix such as `foo.` or `bar.` to the mock `/dns-query` URL, starts a daemon, runs `ipfs resolve /ipns/...`, and checks output or failure. State is mock request history plus node config/cache. Dependencies include `github.com/miekg/dns`, `httptest`, base64url DNS wire encoding, and the CLI harness. Risks include resolver behavior changing between GET and POST, DNS name normalization/trailing dots, and reliance on a fixed CID in DNSLink. Test signal confirms both successful DNSLink resolution and proper error propagation while still proving the DoH endpoint was queried.
