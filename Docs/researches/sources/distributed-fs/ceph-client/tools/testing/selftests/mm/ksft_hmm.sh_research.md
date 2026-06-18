# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_hmm.sh

## Purpose
Wrapper entry point for the MM selftest `hmm` category.

## Important APIs, types, and functions
The script is a four-line shell wrapper invoking `./run_vmtests.sh -t hmm`.

## Control flow
It delegates to the runner's HMM target, which includes the `hmm-tests` binary when the test module/devices are available.

## State and persistence behavior
No local state is changed by the wrapper.

## Dependencies and integration points
Requires `run_vmtests.sh`, HMM selftest binaries, and loaded `/dev/hmm_dmirror*` test devices for meaningful execution.

## Risks and edge cases
The wrapper cannot distinguish feature skips from failures; it reports the runner's status.

## Test signals
Success is the runner completing the HMM target successfully.
