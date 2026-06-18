<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts.go -->
# sources/cloud-native/containers-storage/internal/opts/opts.go

## Purpose
`opts.go` implements reusable command/config option value types and validators.

## Important APIs, Types, And Functions
`ListOpts`, `NamedListOpts`, `MapOpts`, `NamedMapOpts`, `FilterOpt`, `ValidatorFctType`, and `ValidatorFctListType` are the main types. Methods support `Set`, `Delete`, `Get`, `GetAll`, `GetAllOrEmpty`, `GetMap`, `Len`, `Type`, `Name`, `String`, and filter `Value`. Validators include `ValidateIPAddress`, `ValidateLabel`, and `ValidateSysctl`.

## Control Flow
List and map setters optionally normalize input through a validator, then append or split key/value data. `ValidateIPAddress` trims and parses with `net.ParseIP`. `ValidateLabel` requires at least one `=`. `ValidateSysctl` allows a fixed set of kernel keys plus `net.` and `fs.mqueue.` prefixes. `FilterOpt.Set` parses `key=value` filter strings into `Args`.

## State And Persistence
All state is in-memory. List options can wrap caller-owned slices by pointer; map options can wrap caller-owned maps.

## Dependencies And Integration Points
These types are typically used as flag values or configuration parsing helpers. `FilterOpt` delegates to `parse.go`'s `Args`.

## Risks And Edge Cases
`MapOpts.Set` accepts strings without `=` and stores an empty value. `ListOpts.GetAll` returns the underlying slice, not a defensive copy. `ValidateSysctl` uses `strings.Split` rather than `Cut`, so values containing `=` are still accepted as long as the key is allowed.

## Test Signals
`opts_test.go` covers IP validation, map/list option behavior, label validation, and named option wrappers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts.go -->
