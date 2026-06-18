# sources/cloud-native/moby/daemon/internal/distribution/config.go

## Purpose
Defines distribution pull/push configuration and adapters from Moby image/layer stores to registry-oriented interfaces.

## APIs, Control Flow, and Integration
`Config` holds auth, progress, registry resolver, event logger, metadata, image, and reference stores. `ImagePullConfig` adds download manager, accepted schema2 config types, and platform. `ImagePushConfig` adds config media type, layer provider, and upload manager. `ImageConfigStore` wraps image config put/get; `PushLayerProvider` and `PushLayer` abstract layer access. `rootFSFromConfig` and `platformFromConfig` parse image JSON, validate OS, and default empty OS to host. Store-layer adapters expose tar stream, size, media type, parent chain, release, and optional distribution descriptor.

## State, Dependencies, and Risks
State lives in image store, layer store, refstore, and metadata store. Risks include platform defaulting to host for missing OS, only uncompressed tar support from layer store, and release ownership across parent adapters. This file is central to pull/push integration but tested indirectly.
