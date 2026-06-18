# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_stress.sh

## Purpose

`test_stress.sh` is a tiny wrapper that runs the core cgroup test under concurrent stressors. The complete 4-line script was read.

## Important APIs, Types, and Functions

It invokes `./with_stress.sh -s subsys -s fork ${OUTPUT:-.}/test_core`.

## Control Flow

The script delegates all behavior to `with_stress.sh`, selecting subtree-control toggling and fork-loop stress while repeatedly running the built `test_core` binary from `OUTPUT` or the current directory.

## State and Persistence Behavior

State changes come from `with_stress.sh` and `test_core`: cgroup subtree-control toggles, forked `/usr/bin/true` processes, and core test cgroup mutations.

## Dependencies and Integration Points

It depends on bash, `with_stress.sh`, a built `test_core` binary, and cgroup v2 support required by the underlying stress harness.

## Risks and Edge Cases

If `OUTPUT` points to the wrong build directory or `test_core` is absent, the wrapper fails. Stress can amplify timing sensitivity in `test_core`.

## Test Signals

The only direct signal is the exit code from `with_stress.sh`; success means `test_core` repeatedly passed while the selected stressors ran.
