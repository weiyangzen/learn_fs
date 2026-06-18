# sources/distributed-fs/ipfs-kubo/test/cli/api_file_test.go

Purpose: integration test for daemon readiness ordering of `$IPFS_PATH/api` and `$IPFS_PATH/gateway` address files. It guards tools such as systemd path units that react as soon as those files appear.

Important test: `TestAddressFileReady` has `api file` and `gateway file` subtests. Each starts `ipfs daemon` in the background using `(*exec.Cmd).Start` instead of the harness helper that waits for readiness. It polls for the address file up to 100 times with 100 ms sleeps, then immediately reads the address and performs an HTTP request.

Control flow for API extracts IP and TCP port from the multiaddr and posts to `/api/v0/id`; gateway reads the URL from the `gateway` file and GETs `/ipfs/bafkqaaa`. State is daemon-managed repo address files and live HTTP listeners. Dependencies include `net/http`, `os.Stat`, multiaddr protocol values, and harness process management. Risks include timing flakes on slow hosts, assumption of IPv4/TCP address extraction for API, and external HTTP server readiness subtleties. Test signal is direct: file existence must imply immediate successful HTTP status 200.
