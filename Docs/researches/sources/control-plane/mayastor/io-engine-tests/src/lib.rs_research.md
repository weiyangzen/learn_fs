<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/lib.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/lib.rs

Purpose: Root of the io-engine test support library, exporting modules and host/SPDK utility functions used across integration tests.

Important APIs: exports bdev, compose, fio, nexus, nvme/nvmf, pool, replica, snapshot, fault-injection, and single-thread SPDK test support. Defines retry, reactor polling macros, `test_init!`, global `MSTEST`, logging/CPS initialization, file/block-device helpers (`dd`, `truncate`, loopdev, mkfs, fsck, mount, cmp), fio verification scripts, device comparison, URI path extraction, rebuild waiting, RDMA rxe setup/cleanup, composer initialization, JSON formatting, UUID generation, and diagnostic printing.

Control flow: many helpers shell out through `Command` or `run_script`, assert success, and print command output. `wait_for_rebuild()` watches a rebuild job notification channel from an unaffinitized mthread while polling the reactor. `composer_init()` initializes composer from the mayastor source directory.

State and dependencies: mutates host files, loop devices, mounts, RDMA links, `/tmp/__test`, DPDK runtime directories, global logger, SPDK CPS, and Mayastor environment.

Risks and test signals: this file intentionally panics on missing prerequisites. External binaries, root privileges, network route discovery, and timing make failures environmental. The top comment notes a future need to return errors instead of asserting.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/lib.rs -->
