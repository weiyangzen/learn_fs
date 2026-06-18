# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/rootPlugin.py

## Purpose
Provides a tc-testing plugin that enforces root privileges before the suite runs.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` sets `sub_class` to `root/SubPlugin` and overrides `pre_suite()`. It uses `os.geteuid()` and exits with status `1` when not root.

## Control Flow
At suite start, it calls the base `pre_suite()` then checks effective uid. Non-root execution prints an error to stderr and terminates the runner.

## State And Persistence
No persistent state beyond base plugin args and suite metadata.

## Dependencies And Integration Points
Used by the tc-testing runner when root-only operations such as namespace, tc, netfilter, or BPF tests are enabled.

## Risks
It exits immediately rather than returning a kselftest skip result, so non-root runs may appear as failures depending on the caller. It does not check specific capabilities as an alternative to uid 0.

## Test Signals
Root runs continue into cases; non-root runs stop with `This script must be run with root privileges`.
