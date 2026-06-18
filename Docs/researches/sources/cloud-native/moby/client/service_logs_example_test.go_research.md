# sources/cloud-native/moby/client/service_logs_example_test.go

## Purpose
Provides public example documentation for consuming service logs from the Go client.

## APIs, Types, And Functions
`ExampleClient_ServiceLogs` demonstrates `client.NewClientWithOpts`, `Client.ServiceLogs`, `ServiceLogsOptions`, context timeouts, and copying the returned stream to standard output with `io.Copy`.

## Control Flow, State, And Integration
The example creates a context, requests logs for a named service, handles the returned `io.ReadCloser`, defers close, and streams bytes to `os.Stdout`. It is documentation-oriented and does not persist state, but it shows the intended resource-management pattern for callers.

## Risks And Test Signals
The signal is compile-time example validity and API ergonomics. It highlights the need for callers to close streams and manage cancellation; failures would indicate changed constructor names, option fields, or result type behavior.
