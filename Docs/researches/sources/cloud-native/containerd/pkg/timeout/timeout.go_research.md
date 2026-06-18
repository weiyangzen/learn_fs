<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/timeout/timeout.go -->
# sources/cloud-native/containerd/pkg/timeout/timeout.go

## Purpose
Global registry of named timeout durations with context helper.

## Important APIs, Types, And Functions
DefaultTimeout, Set, Get, WithContext, and All.

## Control Flow
Set stores a duration under a key. Get returns key value or DefaultTimeout. WithContext creates context.WithTimeout using Get. All returns a copy of the map.

## State And Persistence
Process-global timeout map protected by RWMutex.

## Dependencies And Integration Points
Used by packages that need configurable operation timeouts without passing durations everywhere.

## Risks And Edge Cases
Global mutable state can leak between tests or subsystems; All returns a copy to avoid external mutation.

## Test Signals
No local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/timeout/timeout.go -->
