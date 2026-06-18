<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh

## Purpose

`zram02.sh` tests zram as swap. It creates a small zram device, configures memory limits, runs `mkswap`, enables swap, disables swap, and cleans up.

## Important APIs, Types, and Functions

The script sources `zram_lib.sh`, sets `dev_num=1`, `zram_max_streams=2`, `zram_sizes=1048576`, and `zram_mem_limits=1M`, then calls library helpers `check_prereqs`, `zram_load`, `zram_max_streams`, `zram_set_disksizes`, `zram_set_memlimit`, `zram_makeswap`, `zram_swapoff`, and `zram_cleanup`.

## Control Flow and State

Flow is linear and cleanup is explicit at the end. State is inherited from `zram_lib.sh`, especially `dev_makeswap`, `dev_start`, `dev_end`, module-load mode, and sysfs-control mode.

## Dependencies and Integration Points

It depends on root privileges, zram sysfs, `mkswap`, `swapon`, `swapoff`, and module or zram-control device creation. It is invoked by `zram.sh` and registered as a support file by the Makefile.

## Risks and Test Signals

Risks include active swap preventing cleanup, missing swap utilities, small memory limits causing setup failures, and failure not reflected in `ERR_CODE` for some library echo-only failures. Passing output ends with `zram02 : [PASS]` after swapoff and cleanup messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram02.sh -->
