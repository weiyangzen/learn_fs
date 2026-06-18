# sources/cloud-native/cri-o/test/mocks/ociartifact/ociartifact.go

## Purpose
Generated GoMocks for OCI artifact helpers and libartifact store access.

## Important APIs, Types, And Functions
`MockImpl` covers manifest instance selection and manifest retrieval. `MockLibartifactStore` covers inspect, list, pull, remove, and system context.

## Control Flow
Each method records or satisfies GoMock expectations with typed return values.

## State And Persistence
No real artifact storage. In-memory mock state only.

## Dependencies And Integration Points
Used by tests around OCI artifact pulling/listing/removal and seccomp artifact integration. Imports digest, libimage, libartifact, manifest, and containers/image types.

## Risks And Test Signals
Cannot validate real artifact store persistence or registry semantics. Interface drift requires regeneration.
