# sources/cloud-native/containerd/core/transfer/registry/registry.go

## Purpose
This file implements an OCI registry transfer endpoint that can resolve, fetch, push, provide credentials, configure hosts, and serialize itself for proxy transfer.

## Important APIs, Types, and Functions
Options configure headers, credentials, hosts directory, default scheme, HTTP debug/trace, and client log stream. `NewOCIRegistry` builds a Docker resolver. `OCIRegistry` implements `ImageFetcher`, `ImagePusher`, `ImageResolverOptionSetter`, string/image helpers, and stream-aware marshal/unmarshal. `credCallback` implements remote credential requests over a stream.

## Control Flow
Creation builds `config.HostOptions`, including credential callbacks and HTTP debug hooks, then creates a Docker resolver. Pull uses `Resolve` and `Fetcher`; push uses `Pusher`, appending the descriptor digest to tag-only refs. `MarshalAny` serializes headers and config, opens auth/log streams when needed, and serves credential requests in a goroutine. `UnmarshalAny` reconstructs host options, installs a streamed credential callback, and configures debug output.

## State and Persistence
State is in-memory registry configuration, resolver, optional stream handles, and credentials helper. It does not persist registry data locally.

## Dependencies and Integration Points
Uses containerd remotes/docker resolver, registry host config, transfer plugins, streaming byte streams, HTTP debugging, transfer protobuf types, and transfer local pull/push.

## Risks
Credential callbacks use `context.Background` in resolver host options and serialize requests with a mutex. HTTP debug log streaming requires closing writers on context cancellation. Header map conversion keeps only `Header.Get` values, not all repeated values.

## Test Signals
Indirectly exercised by pull/push integration, proxy transfer, and credentialed registry tests outside this subset.
