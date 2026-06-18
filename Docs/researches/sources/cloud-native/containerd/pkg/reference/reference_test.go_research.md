<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference_test.go -->
# sources/cloud-native/containerd/pkg/reference/reference_test.go

## Purpose
Table-driven tests for the schema-less reference parser and Spec helper methods.

## Important APIs, Types, And Functions
TestReferenceParser defines cases covering Normalized, Digest, Hostname, Expected Spec, and expected errors.

## Control Flow
Each case calls Parse, verifies exact error identity, compares returned Spec, applies default normalization, and checks String, Digest, and Hostname.

## State And Persistence
No persistent state; tests are pure.

## Dependencies And Integration Points
Depends on opencontainers/go-digest and testing. Exercises reference.go directly.

## Risks And Edge Cases
The table documents intentionally accepted inputs such as missing object and partial digest; future stricter parsing must update expectations deliberately.

## Test Signals
Strong direct unit coverage for all exported behavior in reference.go.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference_test.go -->
