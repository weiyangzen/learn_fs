<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/errors.go -->
# sources/cloud-native/moby/daemon/pkg/registry/errors.go

## Purpose
Provides registry-specific error wrappers with Docker API classification markers.

## Important APIs, Types, And Functions
`translateV2AuthError`, `invalidParam`, `invalidParamf`, `invalidParamWrapf`, and wrapper types `unauthorizedErr`, `invalidParameterErr`, `systemErr`, and `errUnknown`.

## Control Flow
`translateV2AuthError` unwraps URL and distribution errcode errors and maps unauthorized responses to `unauthorizedErr`. Invalid parameter helpers wrap errors while preserving unwrap behavior.

## State, Dependencies, And Integration Points
No state. Error wrappers integrate registry/auth/config code with daemon API error classification.

## Risks And Test Signals
Correct behavior depends on `errors.As`/`errors.Is` through nested distribution errors. Config tests assert invalid-argument classification; auth error translation has less direct coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/errors.go -->
