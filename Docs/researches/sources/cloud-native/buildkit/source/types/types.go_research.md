# sources/cloud-native/buildkit/source/types/types.go

## Purpose
Centralizes string constants for supported source schemes.

## Important APIs, Types, And Functions
- Constants include docker image, docker image blob, git, local, http, https, oci-layout, and oci-layout blob schemes.

## Control Flow
No control flow. Source backends import these constants to advertise and validate schemes.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by git, HTTP, local, OCI, and blob-fetch related code to keep scheme strings consistent.

## Risks And Edge Cases
Changing these string constants is a compatibility break for LLB source identifiers and frontend attrs.

## Test Signals
Indirectly tested by source parsing and backend registration tests across the codebase.
