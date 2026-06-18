## sources/distributed-fs/ipfs-kubo/test/dependencies/ma-pipe-unidir/main.go

Purpose: one-way multiaddr pipe used by transport tests to send stdin over a `manet` connection or receive a connection to stdout.

Important APIs and control flow: `Opts` tracks `--listen/-l` and `--pidFile`. `app` parses flags, validates mode (`send` or `recv`) and multiaddr, either listens and accepts or dials, optionally writes a pid file while active, then copies data with `io.Copy`. `main` exits with `app`'s status. State is limited to the optional pid file, removed via `defer`.

Dependencies and integration points: uses `go-multiaddr` and `go-multiaddr/net`; shell tests can use it for raw multiaddr transport assertions independent of Kubo's CLI.

Risks: error handling intentionally collapses most failures to exit 1 without diagnostics, which keeps scripts simple but makes debugging harder. Listener accept is blocking and needs external timeout or process cleanup. Test signals are successful byte transfer and pid-file lifecycle.
