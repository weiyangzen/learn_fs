<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go

## Purpose
Defines typed driver API errors that participate in Moby error classification through marker methods.

## Important APIs, Types, And Functions
`ErrNoNetwork` and `ErrNoEndpoint` implement `NotFound`. `ErrEndpointExists` and `ErrActiveRegistration` implement `Forbidden`. `ErrNotImplemented` implements `NotImplemented`. Each has an `Error` string.

## Control Flow
Driver and registry code return these errors; higher layers classify them through marker methods rather than string matching.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by network drivers, controller, and error-response layers that understand Moby error marker interfaces.

## Risks And Edge Cases
Error messages are human-readable but not structured. `ErrEndpointExists` says only one endpoint allowed, which may not describe every driver.

## Test Signals
Error classification tests should assert marker methods produce expected HTTP/API categories.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go -->
