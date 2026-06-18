# sources/cloud-native/cri-o/internal/ociartifact/artifact.go

## Purpose
Wraps `libartifact.Artifact` with CRI-O metadata: root path, parsed named reference, pinned status, digest accessors, canonical naming, and CRI image projection.

## Important APIs and Control Flow
`unknownRef` is a fallback named reference. `Artifact` embeds libartifact data and stores `rootPath`, `namedRef`, and `pinned`. `Store.newArtifact` parses artifact names when present, falls back to `unknown`, and combines forced pinning with regex-based pinning. `Reference`, `CanonicalName`, `Digest`, `RootPath`, and `CRIImage` expose metadata; `CRIImage` maps digest to CRI image ID, size to total artifact size, tag when the reference is tagged, canonical repo digest, and pinned flag.

## Integration, Risks, and Tests
Used by artifact listing/status and datastore reads. Bad artifact names are tolerated with warnings but produce `unknown@digest` canonical names. Pinning depends on `Store.isArtifactPinned`. No direct tests in this subset target this wrapper.
