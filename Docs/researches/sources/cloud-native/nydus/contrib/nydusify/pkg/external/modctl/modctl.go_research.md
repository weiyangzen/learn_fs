# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl.go

Purpose: implements a filesystem-backed external snapshotter backend handler for model-control registry layout data, converting OCI model tar layers into backend blob/chunk metadata.

Important APIs/types/functions: constants for registry blob/repo paths and model media types, `Handler`, `blobInfo`, `chunk`, `Object`, `Option`, `NewHandler`, `GetOption`, `Handle`, `Backend`, `GetConfig`, `GetLayers`, `convertToBlobs`, `needIgnore`, and `readTarBlob`.

Control flow: `NewHandler` initializes manifest and blob maps from a local registry root. `Handle` ignores irrelevant files, opens a tar blob, extracts tar file offsets, computes object offsets with `backend.SplitObjectOffsets`, and returns chunks carrying blob digest/size/index, file path, chunk size, and compressed offsets. `Backend` returns a registry backend config with converted blobs.

State and persistence: state is held in `Handler` fields parsed from registry files. `mediaTypeChunkSizeMap` is package-global and mutated by `setWeightChunkSize`.

Dependencies and integration points: local Docker registry storage layout, OCI manifest descriptors, tar reader offsets, go-humanize byte parsing, and snapshotter external backend interfaces.

Risks and test signals: `Option.WeightChunkSize` has a misspelled JSON tag. Global chunk-size mutation can leak across handlers/tests. `GetOption` only accepts `host/namespace/image:tag` with exactly three slash parts, excluding deeper namespaces. Offset correctness depends on tar reader seek position semantics.
