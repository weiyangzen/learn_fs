# sources/control-plane/mayastor/scripts/clean-cargo-tests.sh

Purpose: aggressive cleanup script for resources left by io-engine cargo/integration tests.

Important APIs/types/functions: requires `nix-sudo`, disconnects all NVMe controllers, removes ublk devices backed by `/tmp/io-engine-tests/`, removes loop devices and LVM metadata, deletes soft RDMA link `io-engine-rxe0`, kills/removes docker containers and networks labeled by composer, kills target-directory processes, and removes `/var/run/dpdk/*`.

Control flow: scans ublk and loop devices, performs best-effort cleanup with many tolerated failures, restarts docker if network removal fails, and exits `0`.

State/persistence: mutates host kernel devices, docker state, LVM metadata, DPDK runtime files, and `/tmp/io-engine-tests`.

Dependencies/integration: central cleanup hook for cargo/grpc test scripts; depends on jq, losetup, ublk, LVM tools, docker, rdma, and sudo/nix-sudo.

Risks: intentionally destructive for test resources and uses broad process killing under `$ROOT_DIR/target`. Concurrent tests can be disrupted.

Test signals: after running, stale NVMe, ublk, loop, docker, DPDK, and composer resources should be gone.
