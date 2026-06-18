## sources/cloud-native/moby/integration/container/attach_test.go

Purpose: API-level attach behavior tests. `TestAttach` verifies attach response media type differs for TTY and non-TTY containers. `TestAttachDisconnectLeak` is a Linux regression test for goroutine leaks after attach disconnect.

Control flow creates containers through the Go client, calls `ContainerAttach`, and reads `attach.MediaType()`. The leak test starts a fresh daemon to isolate goroutine counts, creates a long-running container, records stable goroutine count, attaches stdout, waits for count increase, closes the attach stream, then polls for the original count.

State includes container config TTY flag, attach HTTP connection, daemon goroutine count, and a dedicated daemon lifecycle. Dependencies include API client, internal container/system helpers, `daemon.New`, `poll`, and Linux skip. Risks are goroutine-count noise, timeout sensitivity, and attach stream cleanup. Test signals are media types `application/vnd.docker.multiplexed-stream` or raw stream and goroutine count returning to baseline.
