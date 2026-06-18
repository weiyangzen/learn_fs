# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-callbacks.sh

## Purpose

`test-callbacks.sh` validates livepatch object callbacks for vmlinux and target modules across load order, unload order, failed pre-patch callbacks, busy transitions, multiple livepatches, and atomic replacement.

## Important APIs, Types, and Functions

It uses harness functions from `functions.sh` and modules `test_klp_callbacks_demo`, `test_klp_callbacks_demo2`, `test_klp_callbacks_mod`, and `test_klp_callbacks_busy`. It manipulates `pre_patch_ret`, `block_transition`, and `replace` module parameters.

## Control Flow and State

The script runs named scenarios with `start_test()`, then loads/unloads target modules and livepatches in precise orders. It expects callback log lines for module states `COMING`, `LIVE`, and `GOING`, intentionally stalls a transition with a busy worker, and verifies which pre/post patch or unpatch callbacks are skipped or executed.

## Dependencies and Integration Points

It depends on the callback demo modules, livepatch transition machinery, module notifier handling, dmesg filtering, and sysfs `transition`/`enabled`.

## Risks and Test Signals

Risks include callback ordering regressions, failure cleanup leaks, stalled transition reversal bugs, and atomic replace executing callbacks it should bypass. Signals are exact dmesg transcripts for each scenario and successful module reference cleanup.
