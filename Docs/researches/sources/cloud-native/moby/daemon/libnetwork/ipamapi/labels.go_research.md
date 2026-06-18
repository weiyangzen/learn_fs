# sources/cloud-native/moby/daemon/libnetwork/ipamapi/labels.go

## Purpose
Defines reserved option label strings for libnetwork IPAM behavior.

## Important APIs, Types, And Functions
- `Prefix` is the reserved `com.docker.network` label namespace.
- `AllocSerialPrefix` is `com.docker.network.ipam.serial`, used to request serial/first-available allocation ordering.

## Control Flow
No runtime flow exists. Callers pass `AllocSerialPrefix: "true"` in address request options; default IPAM reads it in `addrSpace.requestAddress`.

## State And Persistence
No state. The string can be persisted in options maps or passed through remote IPAM requests.

## Dependencies And Integration Points
Default IPAM tests and allocation code use this label. Windows tests also pass other IPAM option labels through maps.

## Risks
Because labels are stringly typed, misspelling or non-`"true"` values silently fall back to non-serial behavior in default IPAM.

## Test Signals
`allocator_test.go` and `parallel_test.go` use `AllocSerialPrefix` to verify serial allocation/release behavior and concurrent allocation without duplicates.
