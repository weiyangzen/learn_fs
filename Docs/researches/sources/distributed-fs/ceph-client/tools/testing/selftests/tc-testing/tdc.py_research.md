# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.py

## Purpose
Implements the main Linux traffic-control unit test driver. It discovers JSON test cases, loads required plugins, substitutes configured command names, executes setup/command/verify/teardown stages, checks results with regex or JSON matching, and emits TAP or xUnit output.

## Important APIs, Types, and Functions
Important types are `PluginDependencyException`, `PluginMgrTestFail`, and `PluginMgr`. Core functions include `replace_keywords`, `exec_cmd`, `prepare_env`, `verify_by_json`, `find_in_json*`, `run_one_test`, `prepare_run`, `test_runner`, `mp_bins`, `test_runner_mp`, `test_runner_serial`, `load_from_file`, `set_args`, `check_default_settings`, `generate_case_ids`, `filter_tests_by_id`, `filter_tests_by_category`, `get_test_cases`, `set_operation_mode`, and `main`.

## Control Flow
`main()` enforces Python 3.8, raises `RLIMIT_NOFILE`, builds the parser, loads plugins, parses arguments, checks configured tool paths, and calls `set_operation_mode()`. Test discovery loads JSON from `tc-tests` or user-provided files/directories, filters by category or ID, generates IDs if requested, then executes serially or in batches. `run_one_test()` mutates per-test `NAMES`, calls plugin hooks, runs setup, command under test, verify command, and teardown, then restores names. Multiprocess mode splits namespace-safe tests from serial tests and caps workers at four.

## State and Persistence Behavior
Global `NAMES` and `ENVIR` come from `tdc_config.py` plus local overrides. Per-test state is temporarily written into `NAMES` (`TESTID`, randomized namespace/device suffixes). Result state accumulates in `TestSuiteReport` and may be persisted to `test-results.tap`, `test-results.xml`, or `--outfile`. `generate_case_ids()` edits JSON files when blank IDs exist and `--id` is requested.

## Dependencies and Integration Points
Depends on `TdcPlugin`, `TdcResults`, `tdc_config`, `tdc_helper`, plugin directories `plugin-lib` and `plugin-lib-custom`, Python `subprocess`, `multiprocessing.Pool`, and external tools such as `tc`, `ip`, and `ethtool`. It integrates with kernel selftest result conventions through exit codes 0/1/4 and TAP/xUnit formatters.

## Risks and Edge Cases
Commands run with `shell=True`, so test JSON must be trusted. Plugin discovery has a suspicious `plugin_instances` initialization path in `__init__` that treats a list-like object as a dict, while normal required-plugin loading appends tuples. JSON matching has typo paths (`outputJSON`/`matchJSON` and `rest`) that can raise if type mismatches hit those branches. Timeout handling sets return code 255 but does not kill the child explicitly. Multiprocess execution shares plugin manager and args through globals and relies on pickling result data only.

## Test Signals
Useful signals are duplicate ID detection, category and ID filtering, plugin dependency loading, namespace tests in serial and multiprocess mode, JSON and regex verification failures, setup/teardown failure handling, output file ownership under sudo, and proper skip behavior for device-dependent flower tests.
