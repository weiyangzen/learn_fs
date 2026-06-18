<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/registry/registry.go -->
# sources/cloud-native/moby/api/types/registry/registry.go

## Purpose
ServiceConfig stores daemon registry services configuration.

## Important APIs, Types, And Functions
- Exported types: ServiceConfig, IndexInfo, DistributionInspect.
- `ServiceConfig` fields include InsecureRegistryCIDRs, IndexConfigs, Mirrors.
- `IndexInfo` fields include Name, Mirrors, Secure, Official.
- `DistributionInspect` fields include Descriptor, Platforms.
- Wire JSON fields include IndexConfigs, InsecureRegistryCIDRs.
- Source comments highlight: ServiceConfig stores daemon registry services configuration. IndexInfo contains information about a registry RepositoryInfo Examples: { "Index" : { "Name" : "docker.io", "Mirrors" : ["https://registry-2.docker.io/v1/", "https://registry-3.docker.io/v1/"], "Secure" : true, "Official" : true, }, "RemoteName" : "library/debian", "LocalName" : "debian", "CanonicalName" : "docker.io/debian" "Official" : true, } { "Index" : { "Name" : "127.0.0.1:5000", "Mirrors" : [], "Secure" : false, "Official" : false, }, "RemoteName" : "user/repo", "LocalName" : "127.0.0.1:5000/user/repo", "CanonicalName" : "127.0.0.1:5000/user/repo", "Official" : false, } DistributionInspect describes the result obtained from contacting the registry to retrieve image metadata

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Imports: `net/netip`, `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/registry/registry.go -->
