<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config

## Purpose

The zram selftest `config` declares kernel configuration requirements for running the zram tests.

## Important APIs, Types, and Functions

The file sets `CONFIG_ZSMALLOC=y` and `CONFIG_ZRAM=m`, indicating the allocator must be built in and zram should be available as a module for the older module-loading path.

## Control Flow and State

There is no executable flow. The file is consumed by kselftest configuration tooling.

## Dependencies and Integration Points

It integrates with kernel selftest config fragment handling and the zram shell tests, which call `modprobe zram` and manipulate `/sys/block/zram*`.

## Risks and Test Signals

Risks include mismatches with kernels that build zram in or provide only zram-control hotplug. The shell library handles some variants, but this fragment documents the expected testable configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/config -->
