<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/history.go -->
# sources/cloud-native/moby/daemon/container/history.go

## Purpose
Provides sorting for containers by creation time descending.

## Important APIs, Types, And Functions
`History` implements `sort.Interface` through `Len`, `Less`, `Swap`, plus a `sort` helper.

## Control Flow
`Less` returns true when the second container was created before the first, producing newest-first order.

## State And Persistence Behavior
Sorts the slice in place. No external persistence.

## Dependencies And Integration Points
Used by `memoryStore.List` to return containers ordered by creation date.

## Risks And Test Signals
Risk is unstable ordering for equal timestamps. Memory store tests assert newer containers appear first.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/history.go -->
