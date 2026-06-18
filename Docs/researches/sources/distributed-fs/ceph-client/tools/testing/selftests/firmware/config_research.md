<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config

## Purpose
This file documents the kernel configuration requirements for firmware loader selftests.

## Important APIs, Types, And Functions
It requires `CONFIG_TEST_FIRMWARE=y`, `CONFIG_FW_LOADER=y`, `CONFIG_FW_LOADER_USER_HELPER=y`, `CONFIG_IKCONFIG=y`, `CONFIG_IKCONFIG_PROC=y`, and `CONFIG_FW_UPLOAD=y`.

## Control Flow
The shell library prints this file when prerequisites are missing or `/proc/config.gz` cannot confirm support.

## State And Persistence
It has no runtime state; it is a declarative prerequisite list.

## Dependencies And Integration Points
It integrates with `fw_lib.sh` `print_reqs_exit()` and kselftest config reporting.

## Risks
The config list is broad; some subtests can still run without every option, but missing options cause skips or degraded heuristic detection.

## Test Signals
When the running kernel matches these options, `fw_run_tests.sh` should proceed beyond prerequisite checks instead of returning kselftest skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/config -->
