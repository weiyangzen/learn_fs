# sources/cloud-native/cri-o/test/checkcriu/checkcriu.go

## Purpose
Tiny integration-test helper binary that verifies CRIU support for pod checkpoint/restore tests.

## Important APIs, Types, And Functions
`main()` calls `criu.CheckForCriu(criu.PodCriuVersion)` from `github.com/checkpoint-restore/go-criu/v8/utils`.

## Control Flow
If the check returns an error, `main` panics; otherwise the process exits successfully.

## State And Persistence
No persistence. Reads/probes host CRIU availability through the go-criu utility.

## Dependencies And Integration Points
Called from `test/helpers.bash` `has_criu` to skip or enable CRIU-dependent BATS tests.

## Risks And Test Signals
Panic output is acceptable for a test helper but not user-friendly. Behavior depends on host CRIU install and version.
