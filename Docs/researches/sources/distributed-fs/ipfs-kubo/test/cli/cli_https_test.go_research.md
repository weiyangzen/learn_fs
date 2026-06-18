# sources/distributed-fs/ipfs-kubo/test/cli/cli_https_test.go

Purpose: verifies the CLI uses TLS when `--api` is given HTTPS-style multiaddrs.

Important APIs/functions: `TestCLIWithRemoteHTTPS`, `httptest.NewTLSServer`, `net.SplitHostPort`, `url.Parse`, and `harness.Node.RunIPFS`.

Control flow: for both `/https` and `/tls/http` multiaddr suffixes, the test starts a TLS server that records whether `r.TLS` is populated, initializes a Kubo repo, and runs `ipfs id --api /ip4/127.0.0.1/tcp/<port>/<suffix>`.

State/persistence: only a temporary repo is initialized; no daemon is required. The remote endpoint is an in-process TLS server with a self-signed certificate.

Dependencies/integration: API endpoint multiaddr parsing, HTTP client scheme selection, TLS handshake behavior, and CLI remote API path.

Risks/test signals: expected failure is certificate verification, not a plaintext request. Error text is exact enough to catch regressions but may vary if Go TLS messages change.
