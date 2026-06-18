# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config.py

## Purpose
Provides default TDC command substitution values and environment settings, with optional local override support.

## Important APIs, Types, and Functions
Exports `NAMES`, containing paths and symbolic names such as `TC`, `IP`, `DEV0`, `DEV1`, `DEV2`, `DUMMY`, `ETHTOOL`, `ETH`, `BATCH_FILE`, `BATCH_DIR`, `TIMEOUT`, `NS`, and `EBPFDIR`. Exports `ENVIR`, initially empty unless overridden. It imports `tdc_config_local` if present and merges `EXTRA_NAMES` if defined.

## Control Flow
Import-time code defines defaults, tries to import local overrides, then updates `NAMES` with `EXTRA_NAMES` when available. `tdc.py` imports these globals and later mutates selected names per test.

## State and Persistence Behavior
State is in-process Python module state. There is no file write. Local overrides are intentionally outside this file in `tdc_config_local.py`.

## Dependencies and Integration Points
Integrated directly by `tdc.py`, all JSON command substitutions, and plugin argument checks. It assumes default tool paths such as `/sbin/tc`, `/sbin/ip`, and `/usr/sbin/ethtool`.

## Risks and Edge Cases
Default `ENVIR = {}` means subprocesses may run with a stripped environment unless a local config copies `os.environ`. Hard-coded tool paths can fail on distributions where tools live elsewhere. Missing local overrides are silently ignored.

## Test Signals
Signals include `tdc.py` path validation for `TC` and optional `ETHTOOL`, successful variable substitution in commands, and local override behavior through `EXTRA_NAMES` and `ENVIR`.
