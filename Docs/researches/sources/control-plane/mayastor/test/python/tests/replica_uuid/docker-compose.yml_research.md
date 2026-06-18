# sources/control-plane/mayastor/test/python/tests/replica_uuid/docker-compose.yml

Purpose: docker-compose environment for legacy replica UUID/name compatibility tests. It starts a single `ms0` io-engine service at `10.1.0.2`.

Important configuration: the service matches the standard single-node test stack with ANA/reservation env vars, optional interrupt mode, optional IOQ poll period, `RUST_LOG`, `ASAN_OPTIONS=detect_leaks=0`, static networking, source and `/tmp` mounts, hugepages, `/nix`, SYS_ADMIN/SYS_NICE/IPC_LOCK, and unconfined seccomp.

State and integration: replica UUID tests create a malloc pool and replicas via both old and v2 APIs. The compose file provides the gRPC endpoint and process state required by `common.mayastor` fixtures.

Risks and test signals: because it is single-node, it validates API compatibility and enumeration but not network share behavior. Environment misconfiguration surfaces as fixture startup failures rather than test assertions. Correctness is signaled by successful pool online state and replica enumeration in the Python test.
