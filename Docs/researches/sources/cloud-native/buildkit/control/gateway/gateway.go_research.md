# Research: sources/cloud-native/buildkit/control/gateway/gateway.go

Purpose: implements a gRPC gateway bridge forwarder that routes frontend gateway API calls to the active build's registered `LLBBridgeForwarder` based on build ID in the incoming context.

Important APIs and flow: `GatewayForwarder` wraps a generic registrar keyed by build ID. `Register` registers the LLBBridge gRPC server. `RegisterBuild` and `UnregisterBuild` manage active build forwarders. `lookupForwarder` extracts build ID from context and waits/looks up the matching forwarder, converting canceled lookups into unknown-job errors. All gateway RPC methods call `lookupForwarder` and delegate directly: image/source resolution, solve, file and container filesystem operations, evaluate, ping, return, inputs, new/release container, exec process stream, and warnings.

State and dependencies: state is the registrar of active build IDs to forwarders. It depends on buildid context propagation, frontend gateway interfaces/protobufs, registrar synchronization, errdefs, and gRPC registration.

Risks and test signals: missing or stale build IDs produce wrapped forwarding errors; unregister timing must align with build lifecycle to avoid unknown-job failures. There are no direct tests in this subset, so coverage is mostly through gateway frontend integration.
