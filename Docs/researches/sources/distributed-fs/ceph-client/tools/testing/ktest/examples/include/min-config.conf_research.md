# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/min-config.conf

## Purpose

This include defines example `make_min_config` workflows for deriving a small bootable or test-capable kernel config for a target. It is intended for long-running ktest sessions that repeatedly remove candidate config options and verify whether the machine still boots or can run a simple SSH test.

## Important APIs, Types, And Data

The file exposes two conditional test sections. When `${TEST} == min-config`, it sets `TEST_TYPE=make_min_config`, `OUTPUT_MIN_CONFIG=${CONFIG_DIR}/config-new-min-net`, `IGNORE_CONFIG=${CONFIG_DIR}/config-skip-net`, `MIN_CONFIG_TYPE=test`, `TEST=${SSH} echo hi`, and `USE_OUTPUT_MIN_CONFIG=1`. When `${TEST} == min-config && ${MULTI}`, it creates a second `make_min_config` test writing `${CONFIG_DIR}/config-new-min`, using `${CONFIG_DIR}/config-skip`, and starting from `${CONFIG_DIR}/config-new-min-net`.

## Control Flow

`ktest.pl` parses the include and adds one or two tests depending on `TEST` and `MULTI`. Execution later flows through `make_min_config()`: build `allnoconfig`, read Kconfig dependencies, compare the starting minimum config against ignored/default configs, disable one candidate at a time, build and boot/test, then either keep the option in `IGNORE_CONFIG` or remove it from the output minimum config.

## State And Persistence Behavior

This include intentionally creates and updates persistent config files under `${CONFIG_DIR}`. `OUTPUT_MIN_CONFIG` is a resumable product; `IGNORE_CONFIG` records configs found to be required. With `USE_OUTPUT_MIN_CONFIG=1`, reruns automatically continue from existing output instead of prompting. The second test depends on the first test's network-capable output file.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${CONFIG_DIR}` and `${SSH}`. It uses `ktest.pl` support for `TEST_TYPE=make_min_config`, `OUTPUT_MIN_CONFIG`, `IGNORE_CONFIG`, `MIN_CONFIG_TYPE`, `START_MIN_CONFIG`, and `USE_OUTPUT_MIN_CONFIG`. The test-capable first pass requires SSH access after boot; the boot-only second pass only requires console boot detection.

## Risks And Edge Cases

Runs can take many hours or days and involve repeated target reboots. Interruptions are expected, but corrupted or stale `OUTPUT_MIN_CONFIG`/`IGNORE_CONFIG` files can bias future runs. Dependency inference from Kconfig is heuristic and cannot perfectly handle all `select`/default interactions. The second pass assumes `${CONFIG_DIR}/config-new-min-net` exists or is produced by the first pass.

## Test Signals

Dry-run output should show one `make_min_config` test when `MULTI=0` and two when `MULTI=1`. Runtime signals include periodic updates to `config-new-min-net`, `config-skip-net`, `config-new-min`, and `config-skip`, plus ktest logs showing candidate configs being disabled or kept.
