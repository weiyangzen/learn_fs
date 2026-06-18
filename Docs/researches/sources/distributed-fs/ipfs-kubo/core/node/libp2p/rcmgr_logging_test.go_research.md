# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging_test.go

Purpose: verifies aggregated resource-manager warning behavior. Important test is `TestLoggingResourceManager`.

Control flow: under `synctest`, the test builds a resource manager with system connection limits of one, wraps it with `loggingResourceManager` using a one-second interval and observed zap logger, opens three inbound connections, starts logging, advances fake time, and waits until a warning is observed. It asserts the warning reports two protected limit exceedances with the expected libp2p message.

State and persistence: all in-memory; the delegate resource manager is closed with defer.

Dependencies/integration: testing/synctest, libp2p resource-manager/network, multiaddr, zap observer, testify. It guards the operator-facing aggregated log contract and confirms `OpenConnection` errors are counted.

Risks signaled: without aggregation, limit-exceeded logs could be either missing or too noisy; this test ensures a bounded periodic summary appears.
