# sources/cloud-native/stargz-snapshotter/ipfs/converter.go

## Purpose
Converts and pushes a containerd image into an IPFS-addressed form. Converted blobs and the root descriptor are added to IPFS, and blob descriptors receive `ipfs://` URLs.

## Important APIs, Types, And Functions
`Push` calls `PushWithIPFSPath` with default IPFS path behavior. `PushWithIPFSPath` creates a containerd lease, finds the image, resolves IPFS API address, runs a converter with `pushBlobHook`, marshals the converted root descriptor, and adds it to IPFS. `pushBlobHook` uploads descriptor content and sets `URLs`. `GetCID` extracts the first `ipfs://` URL from a descriptor.

## Control Flow
The conversion uses `converter.IndexConvertFuncWithHook`, passing the layer conversion function and a post-convert hook. For each descriptor, the hook chooses the new descriptor if present or copies the original, reads content from containerd, uploads it to IPFS, and annotates the descriptor with the CID URL. The root descriptor JSON is also uploaded, and its CID is returned.

## State And Persistence
Containerd lease state protects content during conversion. IPFS daemon state persists uploaded/pinned blobs. Descriptor URL state records content addressing as `ipfs://<cid>`.

## Dependencies And Integration
Depends on containerd client, content store, image converter package, platforms matcher, local IPFS client, OCI descriptors, and environment/configured `IPFS_PATH`.

## Risks And Test Signals
Risks include uploading large blobs serially through HTTP, relying on IPFS path discovery, and descriptor URL replacement with a single IPFS URL. No direct tests are in this subset; live behavior depends on IPFS client tests and integration conversion tests elsewhere.
