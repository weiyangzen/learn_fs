## sources/distributed-fs/ipfs-kubo/test/dependencies/pollEndpoint/main.go

Purpose: polling utility that waits for a multiaddr endpoint, and optionally an HTTP URL over that endpoint, to become available.

Important APIs and control flow: flags define `-host`, `-tries`, `-tout`, `-http-url`, `-http-out`, and `-v`. `main` parses a multiaddr, optionally enables debug logging, loops `manet.Dial` until success or exhaustion, then, when `-http-url` is set, builds an HTTP client using `connDialer` to dial the same multiaddr and retries `tryHTTPGet` until HTTP 200. `tryHTTPGet` can copy the body to stdout; `connDialer.DialContext` ignores the HTTP transport's network/address and dials the configured multiaddr.

State and dependencies: no persistent state; dependencies include go-log, multiaddr, manet, and net/http. It integrates heavily with `test_launch_ipfs_daemon` and Docker sharness checks.

Risks: only HTTP 200 is accepted, and the helper sleeps the full timeout between retries. A minor code smell is `tryHTTPGet(client, url)` using `*httpURL` rather than its `url` parameter. Test signal is reliable daemon/API/gateway readiness detection.
