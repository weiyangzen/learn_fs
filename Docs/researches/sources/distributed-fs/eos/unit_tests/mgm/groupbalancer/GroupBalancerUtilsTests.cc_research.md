# sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupBalancerUtilsTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupBalancerUtilsTests.cc

Purpose: tests utility functions used by balancer engines and transfer filtering.

Important APIs and types: `calculateAvg`, `is_valid_threshold`, `extract_percent_value`, `extract_commalist_value`, `SkipFileFn`, `NullFilter`, and `PrefixFilter`.

Control flow: average tests update a group-size map and assert exact ratio results. Threshold validation accepts positive numeric strings and rejects zero, negative, float suffixes, and nonnumeric strings. Percent extraction converts config values such as `"5"` to `0.05`, supports defaults, and returns zero for missing keys. Comma-list extraction trims entries into an unordered set. Skip-file tests simulate `getProcTransferNameAndSize` filtering, ensuring a null filter passes all paths and a prefix filter suppresses `/proc/` paths.

State and persistence: no persistent state; helpers operate on local maps and strings.

Dependencies and integration: depends on `BalancerEngineUtils.hh` and `ConverterUtils.hh`. These helpers feed engine configuration and transfer selection behavior.

Risks and test signals: exact floating-point equality is used where values are simple. The tests document accepted config syntax; broadening parser behavior could require updating the test oracle.
