# sources/cloud-native/containerd/plugins/server/internal/listen_windows.go

## Purpose
Classifies local listener addresses on Windows.

## Important APIs, Types, And Functions
`IsLocalAddress` checks for the named-pipe prefix `\\.\pipe\`.

## Control Flow
Server plugins use this helper to choose local named-pipe listener handling versus TCP listening.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by debug and server listener setup on Windows.

## Risks
Only named-pipe addresses are considered local; other Windows path forms are treated as non-local.

## Test Signals
No direct tests.
