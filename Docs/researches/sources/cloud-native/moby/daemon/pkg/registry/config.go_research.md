<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config.go -->
# sources/cloud-native/moby/daemon/pkg/registry/config.go

## Purpose
Defines registry service configuration parsing and validation for Docker Hub defaults, mirrors, insecure registries, certificate locations, and index-name handling.

## Important APIs, Types, And Functions
Key items are `ServiceOptions`, `serviceConfig`, Docker Hub constants, `DefaultV2Registry`, `CertsDir`, `newServiceConfig`, `copy`, `loadMirrors`, `loadInsecureRegistries`, `isSecureIndex`, `isCIDRMatch`, `ValidateMirror`, `ValidateIndexName`, `validateHostPort`, and `getAuthConfigKey`.

## Control Flow
Mirror loading normalizes URLs and removes duplicates. Insecure registry loading adds localhost CIDRs, strips allowed schemes with warnings, stores CIDRs or insecure index configs, and always configures the official index. Security checks prefer explicit index config, then CIDR matching with DNS resolution. Validation rejects mirror credentials, query, fragment, unsupported schemes, invalid hosts, and out-of-range ports.

## State, Dependencies, And Integration Points
State is the daemon registry service config. Depends on `netip`, `reference.DomainRegexp`, rootless config dir detection, and Docker API registry types.

## Risks And Test Signals
DNS lookup affects CIDR matching. Some validation is intentionally legacy-compatible. `config_test.go` covers mirror, insecure registry, service config, and index-name behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config.go -->
