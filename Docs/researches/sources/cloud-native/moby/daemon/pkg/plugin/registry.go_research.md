<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/registry.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/registry.go

## Purpose
Builds registry resolver configuration for plugin pull and push operations.

## Important APIs, Types, And Functions
`scope` builds `repository(plugin):...` auth scopes. `Manager.newResolver`, `registryHTTPClient`, and `Manager.registryHostsFn` configure containerd Docker resolvers and hosts.

## Control Flow
Resolver creation adds Docker user-agent headers and delegates host selection to `registryHostsFn`. Host resolution asks the daemon registry service for endpoints, optionally filters to HTTP fallback, assigns pull/resolve/referrers and push capabilities, builds TLS-aware HTTP clients, and installs an authorizer using username/password or identity token.

## State, Dependencies, And Integration Points
No persistence. It depends on containerd remotes/docker, daemon registry service endpoint lookup, Docker version user-agent, TLS config, and registry auth config.

## Risks And Test Signals
Push fallback only uses HTTP endpoints when requested because containerd push tries the first host. Auth scope must include the plugin classifier or registry authorization fails. Integration tests around pull/push are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/registry.go -->
