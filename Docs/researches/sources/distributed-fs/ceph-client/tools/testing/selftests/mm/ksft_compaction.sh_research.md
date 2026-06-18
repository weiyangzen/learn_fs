# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_compaction.sh

## Purpose
Wrapper entry point for the MM selftest `compaction` category.

## Important APIs, types, and functions
The script is `#!/bin/sh -e` and invokes `./run_vmtests.sh -t compaction`.

## Control flow
Shell startup enables exit-on-error. All behavior is delegated to `run_vmtests.sh`, whose compaction target runs the compaction test for unevictable-page compaction behavior.

## State and persistence behavior
No state is managed by the wrapper. Any sysctl, memory, or log state belongs to `run_vmtests.sh` and the invoked test binaries.

## Dependencies and integration points
Requires execution from the selftests/mm build directory with `run_vmtests.sh` available and executable.

## Risks and edge cases
Because `set -e` is active, any runner failure becomes the wrapper exit status. The wrapper has no argument forwarding or local skip handling.

## Test signals
The wrapper succeeds when `run_vmtests.sh -t compaction` succeeds.
