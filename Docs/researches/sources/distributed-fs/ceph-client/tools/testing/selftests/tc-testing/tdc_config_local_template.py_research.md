# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_config_local_template.py

## Purpose
Template for user- or plugin-specific TDC local configuration. It demonstrates how to preserve the process environment and add custom substitution names or environment variables without editing `tdc_config.py`.

## Important APIs, Types, and Functions
Defines `ENVIR = os.environ.copy()`, reads `LD_LIBRARY_PATH` and `OTHER_LIB`, populates `EXTRA_NAMES` with `SOME_BIN`, and adds Valgrind-related entries to `ENVIR`.

## Control Flow
If copied to `tdc_config_local.py`, it runs at import time from `tdc_config.py`. The base config then merges `EXTRA_NAMES` into `NAMES`.

## State and Persistence Behavior
No runtime persistence. The template itself is a static example; copied local configs can affect every TDC subprocess environment.

## Dependencies and Integration Points
Depends on Python `os`. Integrates with `tdc_config.py` import hooks and all TDC subprocess execution through `ENVIR`.

## Risks and Edge Cases
As a template, it includes example paths that may not exist. Copying it unchanged may add unused Valgrind variables or `SOME_BIN` with an empty base path.

## Test Signals
Signals are successful import as `tdc_config_local`, visible extra substitutions in `args.NAMES`, and subprocess environment values present during command execution.
