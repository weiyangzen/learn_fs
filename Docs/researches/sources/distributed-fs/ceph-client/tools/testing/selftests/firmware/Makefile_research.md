<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile

## Purpose
This Makefile builds and registers firmware loader selftests.

## Important APIs, Types, And Functions
It sets `CFLAGS = -Wall -O2`, declares `TEST_PROGS := fw_run_tests.sh`, `TEST_FILES := fw_fallback.sh fw_filesystem.sh fw_upload.sh fw_lib.sh`, and `TEST_GEN_FILES := fw_namespace`, then includes `../lib.mk`.

## Control Flow
kselftest builds the `fw_namespace` helper and installs/runs `fw_run_tests.sh`, which invokes the shell test set.

## State And Persistence
Build artifacts are generated in the output tree. Runtime state is owned by the scripts and test firmware kernel module.

## Dependencies And Integration Points
It integrates with kselftest and the kernel `test_firmware` module. The paired `config` file lists required firmware loader Kconfig options.

## Risks
The Makefile assumes all shell scripts are copied as `TEST_FILES`; missing one breaks `fw_run_tests.sh` sourcing or subtest invocation.

## Test Signals
Successful build of `fw_namespace` and installed availability of all firmware shell scripts are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/Makefile -->
