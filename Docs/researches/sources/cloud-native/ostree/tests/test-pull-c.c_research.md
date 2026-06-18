<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-c.c -->
# sources/cloud-native/ostree/tests/test-pull-c.c

## Purpose
`test-pull-c.c` unit-tests the C API `ostree_repo_pull` for repeated pulls and recovery after pull errors.

## Important APIs, Types, And Functions
`TestData` owns an `OstreeRepo`. `test_data_init` uses `ot_test_setup_repo`, `ot_test_run_libtest`, `g_file_get_contents`, and `ostree_repo_remote_change` to configure an HTTP `origin` with GPG verification disabled. Tests call `ostree_repo_pull`.

## Control Flow
`test_pull_multi_nochange` pulls `main` three times and expects no errors after the first no-change pull. `test_pull_multi_error_then_ok` loops over successful pulls, repeated failures for `nosuchbranch`, and another successful pull, checking that errors do not poison later API calls.

## State And Persistence
The test creates a temporary repo and fake HTTP remote through libtest. Pulls persist refs and objects in the repo; bad pulls keep errors local.

## Dependencies And Integration Points
It bridges C API consumers with the shell fixture remote and validates remote configuration through `ostree_repo_remote_change`.

## Risks And Test Signals
The critical risk is stale pull state after errors. Passing signals include repeated no-op success and successful pulls after multiple expected failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-c.c -->
