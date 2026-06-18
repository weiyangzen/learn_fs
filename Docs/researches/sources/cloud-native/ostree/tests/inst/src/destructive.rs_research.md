<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/destructive.rs -->
## sources/cloud-native/ostree/tests/inst/src/destructive.rs

Purpose: destructive transactionality stress test that repeatedly interrupts rpm-ostree upgrades to verify staged deployment safety across kills, stops, clean reboots, and forced reboots.

Important APIs/types/functions: enums `PoliteInterruptStrategy`, `ForceInterruptStrategy`, `InterruptStrategy`, and `UpdateResult`; serialized `RebootMark`; `generate_srv_repo()`, `generate_update()`, `upgrade_and_finalize()`, `run_upgrade_or_timeout()`, `parse_and_validate_reboot_mark()`, `validate_live_interrupted_upgrade()`, `impl_transaction_test()`, `suppress_ostree_global_sync()`, and `itest_transactionality()`.

Control flow/state: stores server repo at `/var/tmp/ostree-test-srv` and cycle timing JSON at `/var/tmp/ostree-test-transaction-data.json`. Reboot state is serialized through `AUTOPKGTEST_REBOOT_MARK`. The main loop randomizes interrupt strategy, resets refs/cleanup before each attempt, validates the resulting commit state, and exits after `ITERATIONS` successful accounting cycles.

Dependencies/integration: requires booted OSTree, rpm-ostree, systemd units, `/sysroot`, local HTTP server from `test.rs`, tree mutation from `treegen.rs`, and autopkgtest reboot tools.

Risks/test signals: highly timing-dependent and destructive; random delays and VM load can skew interruption windows. Strong signals are commit-state classification, absence of global sync journal messages, final `ostree fsck`, and structured reboot mark counters.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/destructive.rs -->
