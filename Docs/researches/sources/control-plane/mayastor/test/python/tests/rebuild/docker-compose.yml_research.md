# sources/control-plane/mayastor/test/python/tests/rebuild/docker-compose.yml

Purpose: docker-compose environment for legacy rebuild tests. It launches one `rust:latest` Mayastor/io-engine container named `ms0` on static address `10.1.0.2` in `mayastor_net`.

Important configuration: the command runs `${SRCDIR}/${IO_ENGINE_DIR}/io-engine -g 0.0.0.0 -l ${MS0_CORES:-1,2} -r /tmp/ms0.sock`. Environment enables ANA and reservations, passes optional interrupt-mode and IOQ poll-period knobs, and exposes `RUST_LOG`. It mounts the source tree, `/nix`, hugepages, `/tmp`, and `/var/tmp`.

State, dependencies, and integration: tests use host `/tmp` files as aio children, so the `/tmp` mount is part of the persistence contract. SYS_ADMIN, SYS_NICE, IPC_LOCK, hugepages, and unconfined seccomp are required for io-engine and SPDK behavior. Static networking lets Python fixtures build gRPC handles from docker network metadata.

Risks and test signals: the file is single-node and therefore isolates rebuild behavior from network failures. Runtime correctness depends on environment variables resolving to a valid io-engine binary and host support for hugepages/capabilities. There are no direct assertions in the compose file; its signal is successful service readiness for rebuild feature tests.
