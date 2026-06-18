<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/config/config.go -->
# sources/cloud-native/buildkit/util/resolver/config/config.go

Purpose: defines the TOML-facing registry configuration shape consumed by resolver construction.

Important APIs and types: `RegistryConfig` and `TLSKeyPair`.

Control flow: no functions; struct tags map mirrors, plain HTTP, insecure TLS, CA files, client keypairs, and TLS config directories to BuildKit daemon config.

State and persistence: values are loaded by configuration code elsewhere and passed to `resolver.NewRegistryConfig`.

Dependencies and integration: imported by `util/resolver/resolver.go` and likely by daemon config conversion. The optional bool pointers distinguish unset values from explicit false.

Risks: because fields are simple paths and booleans, validation happens downstream while loading TLS config or constructing registry hosts.

Test signals: `resolver_test.go` indirectly exercises mirror configuration behavior from daemon config.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/config/config.go -->
