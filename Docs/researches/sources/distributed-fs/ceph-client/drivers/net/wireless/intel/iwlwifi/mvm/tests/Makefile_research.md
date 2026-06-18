# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/Makefile

## Purpose

This Makefile wires the MVM KUnit test module into the kernel build. It builds `module.o` and `hcmd.o` into `iwlmvm-tests.o` when `CONFIG_IWLWIFI_KUNIT_TESTS` is enabled.

## APIs, control flow, and dependencies

The file uses standard kbuild variables: `iwlmvm-tests-y` lists objects in the composite test module, and `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS)` conditionally includes it. It depends on the surrounding iwlwifi kbuild context and the KUnit config symbol.

## Risks and test signals

Risks are minimal but include forgotten object additions when new KUnit files are added or missing config dependencies. The signal is a successful kernel/KUnit build with `CONFIG_IWLWIFI_KUNIT_TESTS=y` or `m`, and successful loading/running of the `iwlmvm-tests` suite.
