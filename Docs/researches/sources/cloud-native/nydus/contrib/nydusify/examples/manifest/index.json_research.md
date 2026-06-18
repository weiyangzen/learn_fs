# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/index.json

## Purpose
This JSON file is a sample image index containing both a standard Docker/OCI image manifest and a Nydus manifest for the same platform.

## Important APIs, Types, and Functions
Fields include `schemaVersion` and `manifests`. Each manifest has `mediaType`, `digest`, `size`, and `platform`. The Nydus entry is identified by OCI media type and `artifactType: application/vnd.nydus.image.manifest.v1+json`.

## Control Flow
The file is static documentation/example data. Parser and checker code in the broader nydusify tree use similar structure when handling merged or multi-platform images.

## State, Persistence, and Dependencies
It represents persisted registry index state. No runtime behavior occurs.

## Integration Points
The example supports `--merge-platform` and checker multi-platform concepts by showing source and Nydus artifacts coexisting in an index.

## Risks and Test Signals
Static examples can drift from current OCI artifact conventions. The file is useful for format comprehension but does not validate code by itself.
