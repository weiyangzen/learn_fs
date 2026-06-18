# sources/distributed-fs/beegfs-go/common/registry/capability.go

Purpose: models a component's build metadata and supported feature tree, retrieves it from a remote gRPC endpoint, and validates required features.

Important APIs are `RegistryGetter`, `ComponentRegistry`, `NewComponentRegistry`, `GetComponentRegistry`, `GetBuildInfo`, `GetCapabilities`, `RequireFeature`, `RequireFeatures`, `GetBuild`, `getBuild`, `isRequiredFeatureSupported`, and `isRequiredFeaturesSupported`.

Control flow: `GetComponentRegistry` calls `GetCapabilities`, translates gRPC `Unimplemented` to `ErrCapabilitiesNotSupported`, validates non-nil response and non-zero `StartTimestamp`, and builds a deep-copy registry. Feature checks descend through nested `flex.Feature.SubFeature` maps, with `nil` representing a plain supported feature.

State is immutable by convention: constructor and getters clone protobuf messages and feature maps to avoid callers mutating registry internals. Dependencies include gRPC status/codes, protobuf cloning, and `flex` messages.

Integration points include `CachedComponentRegistry`, feature-gated commands such as RST filter support, and remote services exposing `GetCapabilities`.

Risks: `isRequiredFeatureSupported` checks only path existence and does not inspect payload fields beyond nested maps. Nil available features mean no subfeatures are allowed. Error messages include build labels but not the missing subfeature path except for single-feature checks.

Test signals: `capability_test.go` covers plain and nested feature support and unsupported error wrapping. Cache tests also exercise lazy capability checks.
