<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go -->
# sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go

## Purpose

This test smoke-tests the library example as a real program rather than unit-testing individual helpers. It verifies that `go run main.go` can start temporary Kubo nodes, add and retrieve content, and reach the tutorial's completion path.

## Important APIs, Types, and Functions

`TestExample` uses `exec.Command("go", "run", "main.go")`, streams stdout and stderr through `io.MultiWriter` to both the test process and an in-memory buffer, and sets `GOLOG_LOG_LEVEL=error` to reduce libp2p noise.

## Control Flow, State, and Integration

The test records elapsed runtime, runs the example in the package directory, fails with captured output on command error, and asserts that output contains `All done!`. It exercises the full example's temporary repo creation, plugin setup, node startup, peer connection, UnixFS add/get, and Bitswap fetch paths.

## Dependencies, Risks, and Test Signals

The test depends on the Go toolchain, network loopback, the example fixture directory, and enough time for libp2p setup. It is intentionally broad and can fail from environment issues that unit tests would isolate. The key test signal is the final output string, plus command exit status and elapsed time logs for diagnosing CI hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go -->
