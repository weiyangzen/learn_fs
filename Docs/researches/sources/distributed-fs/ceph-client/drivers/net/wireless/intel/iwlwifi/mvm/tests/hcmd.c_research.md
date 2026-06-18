# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tests/hcmd.c

## Purpose

`hcmd.c` contains a KUnit test for MVM host-command name metadata. It verifies that command-name arrays are sorted by command ID, which supports deterministic lookup behavior in debug/trace helpers.

## Important APIs and control flow

`test_hcmd_names_sorted()` iterates over `iwl_mvm_groups[]`, skips empty arrays, and checks each adjacent command ID with `KUNIT_EXPECT_LE()`. The file registers the case in `hcmd_names_cases`, wraps it in `struct kunit_suite hcmd_names`, and exposes it via `kunit_test_suite()`.

## State, dependencies, and integration

The test has no persistent state. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace, includes `<kunit/test.h>`, `<iwl-trans.h>`, and `../mvm.h`, and depends on exported `iwl_mvm_groups` and `iwl_mvm_groups_size` metadata from the driver.

## Risks and test signals

The test catches unsorted command-name tables but does not verify names, coverage completeness, duplicate IDs, or group ordering. A passing KUnit run for suite `iwlmvm-hcmd-names` is the primary signal; failures identify a table index where command IDs are out of order.
