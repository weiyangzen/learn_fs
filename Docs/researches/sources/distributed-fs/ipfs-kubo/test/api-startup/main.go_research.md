# sources/distributed-fs/ipfs-kubo/test/api-startup/main.go

Purpose: utility program measuring relative startup time of Kubo API and gateway HTTP endpoints.

Important APIs and control flow: starts two goroutines polling `http://127.0.0.1:5001` and `http://127.0.0.1:8080` until each returns a response, sends the timestamp to a buffered channel, waits for both goroutines, reads both timestamps, and logs their difference.

State and persistence: no persistence; loops aggressively until endpoints respond.

Dependencies and integration: intended for test/manual startup measurement against a local daemon exposing default API and gateway ports.

Risks and test signals: no sleep, timeout, response body close, or status filtering, so it can spin hot, hang forever, and leak response bodies in the short run. It logs timing but does not assert success thresholds.
