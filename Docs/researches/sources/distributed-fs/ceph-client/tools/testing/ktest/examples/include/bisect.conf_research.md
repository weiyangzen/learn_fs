# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bisect.conf

## Purpose

This ktest include defines reusable test sections for two bisect-oriented workflows: a normal git bisect driven by ktest build/boot/test results, and a config bisect driven by a known bad `.config` versus a good or minimum config. It is meant to be included by machine-specific files such as `test.conf`, `kvm.conf`, or `vmware.conf` after they set `TEST`, machine access, and default paths.

## Important APIs, Types, And Data

The effective API is the ktest config language consumed by `ktest.pl`: `DEFAULTS IF`, `TEST_START IF`, immediate variables assigned with `:=`, and per-test options assigned with `=`. `RUN_TEST` is a reusable variable defaulting to `${SSH} hackbench 50`. The `TEST == bisect` section sets `TEST_TYPE=bisect`, `BISECT_GOOD`, `BISECT_BAD`, `CHECKOUT`, `BISECT_TYPE=test`, `TEST=${RUN_TEST}`, `BISECT_CHECK=1`, and `MIN_CONFIG=${THIS_DIR}/config-bisect`. The `TEST == config-bisect` section sets `TEST_TYPE=config_bisect`, `CONFIG_BISECT_TYPE=boot`, `CONFIG_BISECT`, and `CONFIG_BISECT_GOOD`.

## Control Flow

`ktest.pl` reads the including file, expands `INCLUDE include/bisect.conf`, evaluates the `DEFAULTS` block if `RUN_TEST` was not already defined, and materializes only the `TEST_START` block whose condition matches the caller's `${TEST}` variable. For a git bisect, execution later flows through `bisect()`, optional good/bad verification, repeated `run_bisect()` build/boot/test attempts, and `git bisect good|bad|skip`. For config bisect, execution flows through `config_bisect()`, oldconfig normalization of good and bad configs, then repeated invocations of `config-bisect.pl`.

## State And Persistence Behavior

The file itself is static. It points ktest at persistent git state in `BUILD_DIR`, a persistent bisect minimum config at `${THIS_DIR}/config-bisect`, bad/good config files under `${THIS_DIR}`, and optional replay state if `BISECT_REPLAY` or `BISECT_START` is uncommented. Runtime state is stored by `ktest.pl` in git bisect metadata, logs, temporary configs, dmesg/test/build logs, and possibly failure directories configured elsewhere.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${SSH}`, `${THIS_DIR}`, `${CONFIG_DIR}`, machine, build, log, and reboot defaults. It integrates with `ktest.pl` options for `bisect`, `config_bisect`, `BISECT_RET_*`, `BISECT_SKIP`, `BISECT_MANUAL`, `CONFIG_BISECT_EXEC`, and target test execution. The default `RUN_TEST` assumes `hackbench` is available on the target over SSH.

## Risks And Edge Cases

The sample commits (`v3.3`, `HEAD`, `origin/master`) are placeholders and can bisect the wrong range if copied unchanged. `BISECT_CHECK=1` is safer but expensive and can mutate hardware state before the real search. `BISECT_SKIP` defaults are nuanced: build/boot failures during test bisects may be skipped unless disabled. Config bisect assumes the bad config is generally a superset of the good config; missing required configs or dependency-selected options can produce inconclusive results.

## Test Signals

Useful validation is `ktest.pl --dry-run <machine.conf>` with `TEST:=bisect` and `TEST:=config-bisect` overrides, checking that exactly the intended `TEST_TYPE`, commits, configs, and `TEST` command resolve. Runtime evidence includes git bisect progress, generated `good_config`/`bad_config` files for config bisect, build/test logs, and final ktest result banners.
