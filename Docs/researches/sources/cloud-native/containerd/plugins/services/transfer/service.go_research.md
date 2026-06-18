# sources/cloud-native/containerd/plugins/services/transfer/service.go

## Purpose
This file implements the gRPC transfer service. It resolves typed source and destination payloads, attaches optional progress streaming, and delegates to registered transfer plugins.

## Important APIs, Types, And Functions
The plugin ID is `transfer` and requires transfer and streaming plugins. `service` stores a slice of `transfer.Transferrer` and a `streaming.StreamManager`. Main functions are `newService`, `Register`, `Transfer`, and `convertAny`. `streamUnmarshaler` lets payload types resolve embedded streams through the stream manager.

## Control Flow
Initialization gathers all transfer plugins and the streaming manager. `Transfer` builds options, including a progress callback that marshals `transferTypes.Progress` and sends it on the named stream. Source and destination are resolved using `tplugins.ResolveType` or plain `typeurl.UnmarshalAny`. The service tries each transferrer until one succeeds, skips `ErrNotImplemented`, and returns unimplemented if none accept the pair.

## State And Persistence
No durable state is owned here. Data movement and persistence are handled by transferrer implementations and stream payloads.

## Dependencies And Integration Points
It integrates transfer plugins, streaming manager, typeurl, OCI descriptor protobuf conversion, log warnings, and gRPC status conversion.

## Risks
Transfer plugin ordering is unspecified. Progress send failures are logged but do not fail the transfer. A progress stream is closed by defer after `Transfer`, so transferrers must not retain the callback asynchronously beyond the call.

## Test Signals
No direct tests are included. End-to-end image/content transfer tests are needed to validate plugin selection and progress behavior.
