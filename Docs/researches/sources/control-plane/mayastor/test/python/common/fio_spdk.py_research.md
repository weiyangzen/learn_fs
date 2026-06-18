# sources/control-plane/mayastor/test/python/common/fio_spdk.py

## Purpose
Builds SPDK fio command strings for direct userspace NVMe/TCP workloads against Mayastor NVMf URIs.

## Important APIs, Types, And Functions
Class `FioSpdk` parses one or more NVMf URIs into SPDK filename descriptors and `build()` returns a command using `LD_PRELOAD=<spdk_nvme>`, `$FIO --ioengine=spdk`, 4 KiB direct IO, iodepth 64, and per-URI `--filename`.

## Control Flow
The constructor normalizes `uris`, parses host/port/subnqn fields, escapes colon characters in NQNs, and stores formatted filenames. `build` resolves `FIO_SPDK` or falls back to `SPDK_ROOT_DIR` or a relative `spdk-rs` build path.

## State And Persistence
Only stores fio command metadata. Persistent effects are produced by fio after test execution.

## Dependencies And Integration Points
Used by nexus and CLI controller tests to generate SPDK fio traffic without kernel NVMe devices. Integrates with SPDK build artifacts, environment variables, and Mayastor NVMf exports.

## Risks
Environment fallback paths are repository-layout sensitive. The command uses `sudo`, `$FIO`, and shell quoting, so test hosts must provide compatible tooling.

## Test Signals
Successful SPDK fio runs validate userspace initiator connectivity, controller stats accounting, and degraded/faulted nexus IO behavior.
