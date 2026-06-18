# sources/cloud-native/moby/integration/internal/network/dns.go

Purpose: lightweight DNS test helper that generates resolv.conf content and starts a minimal UDP DNS responder.

Important APIs and constants: `DNSRespAddr`, `GenResolvConf`, and `StartDaftDNS`.

Control flow: `GenResolvConf` returns a single nameserver line. `StartDaftDNS` listens on UDP address `addr`, starts a goroutine that reads packets, unpacks DNS messages with `miekg/dns`, creates a reply with one A record for each question pointing to `DNSRespAddr`, and writes the response.

State and persistence: opens a UDP socket for the lifetime of the test and closes it through `t.Cleanup`. No persistent state is written.

Dependencies and integration: depends on `github.com/miekg/dns`, `net.ListenPacket`, and testing cleanup. It integrates with network tests requiring deterministic DNS responses.

Risks: the server ignores read/write/unpack/pack errors by continuing, so failures may manifest as client timeouts. It returns A records regardless of question type.

Test signals: helper-only; useful for validating daemon/container DNS plumbing against a predictable local resolver.
