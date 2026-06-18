## sources/cloud-native/moby/daemon/internal/image/rootfs.go

Purpose: Models an image root filesystem as a list of layer DiffIDs and computes chain IDs.

Important APIs/types: `TypeLayers` is the supported rootfs type. `RootFS` has JSON fields `type` and `diff_ids`. `NewRootFS`, `Append`, `Clone`, and `ChainID` are the methods.

Control flow: `Append` appends a diff ID in layer order. `Clone` copies the type and uses `slices.Clone` for DiffIDs. `ChainID` delegates to OCI `identity.ChainID` to compute the top layer chain digest from all diff IDs.

State and persistence: RootFS is persisted inside image config JSON. The order of `DiffIDs` is semantically significant.

Dependencies and integration: Used by image creation, layer store lookups, tar load/save, and builder cache. Depends on daemon layer digest aliases and OpenContainers identity.

Risks: `Append` mutates the receiver; callers sharing a RootFS pointer can accidentally mutate parent images. Empty DiffIDs produce an empty chain ID.

Test signals: Covered indirectly by image and store tests.
