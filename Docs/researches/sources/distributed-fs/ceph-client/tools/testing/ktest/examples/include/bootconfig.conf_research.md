# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bootconfig.conf

## Purpose

This include defines ktest test cases that install bootconfig snippets into a target initrd, reboot or reuse a kernel, and run verifier scripts for tracing-related bootconfig scenarios. It is an example for testing bootconfig scripts rather than for building a new kernel each time.

## Important APIs, Types, And Data

The file defines immediate variables and ktest options: `INITRD`, `BOOTCONFIG`, `BUILD_TYPE`, `ADD_BOOTCONFIG`, `BOOTCONFIG_TEST_PREP`, `CLEAR_BOOTCONFIG`, `DO_TEST`, and `RUN_BOOTCONFIG`. It declares three `TEST_START IF DEFINED RUN_BOOTCONFIG` sections with `TEST_TYPE=test`, distinct `TEST_NAME` values, `BUILD_TYPE=nobuild`, specific `BOOTCONFIG_FILE` and `BOOTCONFIG_VERIFY` values, `ADD_CONFIG=${ADD_CONFIG} ${BOOTCONFIG_PATH}/config-bootconfig`, `PRE_TEST`, `PRE_TEST_DIE=1`, `TEST=${DO_TEST}`, and `POST_TEST=${CLEAR_BOOTCONFIG}`.

## Control Flow

When included, `ktest.pl` creates three test cases if `RUN_BOOTCONFIG` is defined. Each test runs `PRE_TEST` to copy the selected `.bconf` file to the target and use the target `bootconfig` tool to replace/apply it to `${INITRD}`. The test body copies and runs the matching verifier script on the target. `POST_TEST` removes bootconfig data from the initrd after the test.

## State And Persistence Behavior

The runtime state is on the target host: `/tmp/${BOOTCONFIG_FILE}`, `/tmp/${BOOTCONFIG_VERIFY}`, and modifications to `${INITRD}`. `POST_TEST` attempts to clear those bootconfig modifications, but temporary files on the target may remain. ktest logs record prep/test/post-test command output.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${SSH}`, `${SSH_USER}`, and `${MACHINE}`; on an including config for `BOOTCONFIG_PATH`; on `scp`/SSH access; on a target-side bootconfig executable at `${BOOTCONFIG}`; on verifier shell scripts; and on ktest's `PRE_TEST`, `TEST`, and `POST_TEST` hooks. `ADD_CONFIG` integrates with kernel configuration when a build is enabled, but each declared test overrides to `nobuild`.

## Risks And Edge Cases

Because it modifies a real initrd on the target, failed `POST_TEST` cleanup can leave subsequent boots with stale bootconfig settings. `BUILD_TYPE=nobuild` assumes the target kernel/initrd already support bootconfig and tracing. `PRE_TEST_DIE=1` prevents running verifiers after failed preparation, but not all cleanup paths are guaranteed if a critical failure occurs outside normal post-test handling. Missing `BOOTCONFIG_PATH` or verifier files will fail only at runtime/dry-run resolution.

## Test Signals

Dry-run output should show three named bootconfig tests with `nobuild`, `PRE_TEST`, `TEST`, and `POST_TEST` resolved. Runtime success is the verifier exit status plus logs showing bootconfig deletion/addition before testing and deletion afterward. Manual validation can inspect the initrd with `${BOOTCONFIG} -l` or equivalent before and after a run.
