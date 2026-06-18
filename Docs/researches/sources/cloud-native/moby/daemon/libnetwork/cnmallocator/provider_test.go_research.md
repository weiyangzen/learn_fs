<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go

## Purpose
Tests minimal validation behavior for CNM allocator provider driver validation methods.

## Important APIs, Types, And Functions
`TestValidateDriver` runs both `ValidateIPAMDriver` and `ValidateNetworkDriver`, asserting nil is accepted and an empty-name driver returns `codes.InvalidArgument`.

## Control Flow
The table-driven test creates a provider without plugin getter and applies each validator to nil and empty driver values.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses SwarmKit API driver objects, SwarmKit testutils error-code extraction, gRPC codes, and gotest assertions.

## Risks And Edge Cases
It does not cover built-in driver acceptance, plugin lookup, legacy plugin rejection, or ingress-specific validation.

## Test Signals
Passing confirms the provider preserves the required nil/default and empty-name validation contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go -->
