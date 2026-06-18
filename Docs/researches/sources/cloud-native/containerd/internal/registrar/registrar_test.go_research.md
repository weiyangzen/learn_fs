# sources/cloud-native/containerd/internal/registrar/registrar_test.go

## Purpose
Tests registrar reservation and release semantics.

## Important APIs, Types, And Functions
`TestRegistrar` uses a new registrar and checks `Reserve`, `ReleaseByKey`, `ReleaseByName`, and `ReservedErr`.

## Control Flow
The test reserves two mappings, repeats an idempotent reservation, tries conflicting mappings, releases both directions, then reserves new mappings including identical name/key.

## State And Persistence
Mutates in-memory registrar maps.

## Dependencies And Integration Points
Uses Go testing and testify assertions.

## Risks
No concurrent access test is present despite the type being concurrency-safe.

## Test Signals
Good unit signal for core conflict and release behavior.
