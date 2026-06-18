## sources/distributed-fs/ipfs-kubo/test/cli/transports_test.go

Purpose: Go CLI integration coverage for Kubo swarm transport combinations. `TestTransports` creates local harness nodes and verifies the same add/cat and recursive refs workflows over TCP, TCP with TLS disabled so Noise is used, QUIC, QUIC WebTransport, QUIC with announced non-dialable WebTransport addresses, and WebRTC Direct.

Important APIs and control flow: local closures `disableRouting`, `checkSingleFile`, `checkRandomDir`, `runTests`, and `tcpNodes` configure `config.Config`, create random content with `go-test/random` and `random/files`, start daemons, connect peers, and assert retrieval from every node. State is persisted only in temporary harness repositories and their Kubo config files; routing is set to `none` and bootstrap is cleared to force direct transport behavior. Dependencies and integration points include `test/cli/harness`, Kubo `config`, local daemon startup, `ipfs add`, `ipfs cat`, and `ipfs refs -r`.

Risks: all subtests run in parallel and use live daemons, random ports, and local networking, so regressions can be timing-sensitive. The non-dialable announce case is explicitly coupled to Kubo address-selection internals. Test signals are successful daemon connection and byte/refs retrieval under each transport-specific config.
