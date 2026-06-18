# sources/cloud-native/containerd/integration/client/client_ttrpc_test.go

## Purpose
This file integration-tests the TTRPC client utility against containerd's TTRPC endpoint.

## Important APIs, Types, and Functions
Tests cover `ttrpcutil.NewClient`, `Reconnect`, service retrieval, event forwarding, and close behavior.

## Control Flow
Tests skip in short mode, connect to `address + ".ttrpc"`, reconnect where applicable, forward a test event through the events service, close the client, and assert closed-client behavior returns `ttrpc.ErrClosed`.

## State and Persistence
Only transient client connections and a forwarded event envelope are created.

## Dependencies and Integration Points
Uses TTRPC event service API, protobuf timestamp/Any helpers, namespaces, and the shared integration address.

## Risks
Requires the daemon to expose the TTRPC socket and events service. Event forwarding is used as a liveness check, not as persisted event validation.

## Test Signals
Confirms TTRPC connect, reconnect, service use after reconnect, idempotent close, and expected closed error.
