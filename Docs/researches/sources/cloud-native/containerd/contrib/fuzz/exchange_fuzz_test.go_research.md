<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go

## Purpose
Fuzzes content exchange/transfer behavior.

## Important APIs, Types, And Functions
Defines `FuzzExchange`.

## Control Flow
Generates descriptors/content data and drives exchange logic to catch malformed graph or descriptor handling issues.

## State And Persistence
Test-scoped content state only.

## Dependencies And Integration Points
containerd transfer/exchange packages and fuzz headers.

## Risks And Test Signals
Limited semantic assertions; useful for crash/pathological input discovery. Source size reviewed: 57 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/exchange_fuzz_test.go -->
