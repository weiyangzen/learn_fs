<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_unsupported.go -->
# sources/cloud-native/containerd/pkg/sys/oom_unsupported.go

## Purpose
Non-Linux OOM score stubs.

## Important APIs, Types, And Functions
Defines OOMScoreMaxKillable/OOMScoreAdjMax as zero and no-op AdjustOOMScore, SetOOMScore, GetOOMScoreAdj.

## Control Flow
All calls return success or zero immediately.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Maintains cross-platform compilation for callers that adjust OOM scores on Linux.

## Risks And Edge Cases
Silent success can mask unsupported behavior if caller expects enforcement.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_unsupported.go -->
