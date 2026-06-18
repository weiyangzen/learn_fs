# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/manifest.json

## Purpose
This JSON file is a sample Nydus image manifest showing multiple Nydus blob layers followed by a bootstrap layer.

## Important APIs, Types, and Functions
It includes `schemaVersion`, `config`, and `layers`. Blob layers use Nydus blob media type and `containerd.io/snapshot/nydus-blob` annotations. The final bootstrap layer uses a gzip tar media type and annotations including `containerd.io/snapshot/nydus-bootstrap` and `containerd.io/snapshot/nydus-reference-blob-ids`.

## Control Flow
The file is static example data. Manifest checker rules enforce a related invariant: non-final layers are Nydus blobs and the final layer is a bootstrap for non-model artifacts.

## State, Persistence, and Dependencies
It models registry manifest persistence. Digests and sizes are sample identifiers.

## Integration Points
The file documents the shape expected by parser/checker/cache logic and by runtimes consuming Nydus images.

## Risks and Test Signals
The example is only as accurate as its maintenance. It is not executable but helps identify media type and annotation expectations used elsewhere.
