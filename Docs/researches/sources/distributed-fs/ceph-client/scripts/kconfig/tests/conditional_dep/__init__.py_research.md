# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/__init__.py

## Purpose
This pytest module validates conditional dependency output for three scenarios.

## Important APIs, Types, and Functions
The single `test(conf)` calls `conf.oldconfig('test_config1')`, `test_config2`, and `test_config3`, then checks `expected_config1`, `expected_config2`, and `expected_config3`.

## Control Flow
Each oldconfig run starts from a fixture `.config` and must complete successfully.

## State and Persistence
Temporary `.config` output is recreated per call.

## Dependencies and Integration Points
Depends on the conditional dependency Kconfig and fixture config files.

## Risks and Edge Cases
If `Conf._run_conf()` reused mutable `extra_env` across calls unexpectedly, tests could leak environment, but these calls do not pass custom env.

## Test Signals
Pass means conditional dependencies work across all provided bool/tristate combinations.
