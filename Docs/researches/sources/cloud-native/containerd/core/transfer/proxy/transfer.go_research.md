# sources/cloud-native/containerd/core/transfer/proxy/transfer.go

## Purpose
This file implements a client-side transfer proxy that forwards transfer requests over gRPC or TTRPC and bridges progress streams back to local callbacks.

## Important APIs, Types, and Functions
`NewTransferrer` adapts generated clients, client connections, TTRPC clients, or existing transfer services. `proxyTransferrer.Transfer` marshals source and destination endpoints and sends `TransferRequest`. `marshalAny` delegates to stream-aware marshalers when available.

## Control Flow
Transfer options are converted to API options. If progress is requested, a stream is created and a goroutine receives transfer progress protobufs, converts descriptors back to OCI form, and calls the local progress callback. Source and destination are marshaled, wrapped in protobuf `Any`, and sent to the remote transfer service.

## State and Persistence
No durable state. Runtime state includes the transfer client, stream creator, and active progress goroutine.

## Dependencies and Integration Points
Integrates transfer API, streaming interfaces, transfer streaming ID generation, `typeurl`, gRPC/TTRPC adapters, errgrpc normalization, and OCI descriptor conversion.

## Risks
Progress goroutine logs unmarshalling/receive issues but does not fail the transfer. Endpoint marshaling requires all endpoint types to be registered or natively marshalable. Transport error conversion must preserve containerd errdefs semantics.

## Test Signals
Indirectly covered by client transfer API integration and stream tests.
