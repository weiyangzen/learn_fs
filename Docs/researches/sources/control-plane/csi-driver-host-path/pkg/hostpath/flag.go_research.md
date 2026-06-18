# sources/control-plane/csi-driver-host-path/pkg/hostpath/flag.go

## Purpose
This file defines custom command-line flag value types used by the hostpath driver configuration: simulated storage capacity by kind and comma-separated string arrays.

## Important APIs, Types, And Functions
`Capacity` is `map[string]resource.Quantity` and implements `flag.Value` through `Set`, `String`, and `Enabled`. `Set` requires `<type>=<size>`, parses the size with Kubernetes `resource.ParseQuantity`, initializes the map if needed, and overwrites prior values. `StringArray` is `[]string` and implements `Set` by splitting comma-separated values and trimming whitespace, and `String` by formatting the slice.

## Control Flow
The flag package calls `Set` once per supplied flag occurrence. Multiple `--capacity` flags accumulate or overwrite per kind. Multiple `StringArray.Set` calls append values.

## State, Persistence, And Dependencies
These types hold in-memory process configuration only. Capacity values later affect controller `CreateVolume` and `GetCapacity`; they are not persisted except indirectly through volume `Kind` records. Dependencies are Go `flag`, `strings`, `fmt`, `errors`, and Kubernetes resource quantities.

## Integration Points
Deployment manifests pass `--capacity=slow=10Gi` and `--capacity=fast=100Gi` in the distributed plugin. Mutable parameter configuration uses `StringArray` to filter `ControllerModifyVolume` and `CreateVolume` mutable parameters.

## Risks
`StringArray.Set` does not ignore empty entries, so `--flag=` or trailing commas add empty accepted names. `Capacity.Enabled` dereferences the map receiver, so callers must use an initialized variable or addressable zero value as intended. Capacity is simulated and only enforced by driver code.

## Test Signals
Tests should cover valid/invalid capacity strings, multiple capacities, overwrites, binary/decimal quantities, empty string-array entries, whitespace trimming, and `Enabled` for nil and populated maps.
