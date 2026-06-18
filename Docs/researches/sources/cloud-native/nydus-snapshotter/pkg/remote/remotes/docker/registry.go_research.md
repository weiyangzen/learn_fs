# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry.go

## Purpose
Defines registry host configuration, host capability flags, default registry generation, host matching helpers, and registry-host composition.

## Important APIs, Types, And Functions
`HostCapabilities`, `RegistryHost`, `RegistryHosts`, `Registries`, `RegistryOpt`, `WithPlainHTTP`, `WithAuthorizer`, `WithHostTranslator`, `WithClient`, `ConfigureDefaultRegistries`, `MatchAllHosts`, and `MatchLocalhost`.

## Control Flow
`ConfigureDefaultRegistries` returns a resolver function that builds one `RegistryHost` with HTTPS `/v2`, all core capabilities, default client, optional plain HTTP, optional host translation, and Docker Hub translation to `registry-1.docker.io`. `Registries` tries configured registry functions in order and returns the first non-empty result. `RegistryHost.isProxy` determines whether namespace query injection is needed.

## State And Persistence
No persistent state. Functions return immutable host config values except embedded clients/authorizers.

## Dependencies And Integration Points
Registry hosts are consumed by resolver/fetcher/pusher/referrers code. Capabilities control trust boundaries for pull, resolve, push, and referrers operations.

## Risks And Edge Cases
Resolve capability is security-sensitive because a mirror that can return arbitrary tag-to-digest mappings should not be trusted. `MatchLocalhost` handles IPv4/IPv6/ports but intentionally does not support octal/decimal/hex IP forms.

## Test Signals
`registry_test.go` validates capability matching and localhost detection across common host formats and invalid addresses.
