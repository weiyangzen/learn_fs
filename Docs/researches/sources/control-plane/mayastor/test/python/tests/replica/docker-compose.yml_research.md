# sources/control-plane/mayastor/test/python/tests/replica/docker-compose.yml

Purpose: docker-compose fixture for legacy pool and replica BDD tests. It starts one `ms0` io-engine instance at `10.1.0.2`.

Important configuration: the service uses `${MS0_CORES:-1,2}`, static `mayastor_net`, ANA/reservation environment variables, optional interrupt mode, optional NVMe IOQ poll period, and `RUST_LOG`. It mounts the repo, `/nix`, hugepages, `/tmp`, and `/var/tmp`; capabilities and unconfined seccomp match SPDK/io-engine needs.

State and integration: pool tests create malloc or aio-backed pools, and replica tests create malloc-backed LVS pools. The shared `/tmp` mount enables aio image tests. Python fixtures locate `ms0` through docker-compose and create gRPC handles.

Risks and test signals: the single-node setup does not validate multi-node replica sharing, but it keeps pool/replica semantics deterministic. Any missing hugepages, permissions, or wrong `${IO_ENGINE_DIR}` will fail before test logic. The compose file itself has no assertions; readiness and gRPC connectivity are its effective signal.
