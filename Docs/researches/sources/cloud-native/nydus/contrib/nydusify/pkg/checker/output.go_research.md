# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/output.go

## Purpose
This file writes parsed OCI/Nydus image metadata and pulled Nydus bootstrap contents into the checker work directory. It also validates bootstrap diff ID consistency and model artifact subject shape.

## Important APIs, Types, and Functions
`prettyDump` marshals objects as indented JSON to files. `Checker.Output` writes index, manifest, config, and bootstrap artifacts for a parsed image.

## Control Flow
`Output` creates the output directory, writes OCI and/or Nydus index/manifest/config JSON depending on parsed content, pulls the Nydus bootstrap layer when present, decompresses it, unpacks the tar into `nydus_bootstrap`, hashes the uncompressed tar stream, and compares the calculated digest with the last rootfs diff ID except for model artifacts. Model manifests require a subject with image-manifest media type.

## State, Persistence, and Dependencies
Persistent outputs include `oci_index.json`, `nydus_index.json`, `oci_manifest.json`, `oci_config.json`, `nydus_manifest.json`, `nydus_config.json`, and unpacked bootstrap files. Dependencies include JSON, containerd compression, digest, parser, checker tool image type, utils tar unpacking, OCI spec, and model-spec.

## Integration Points
Checker rules expect output artifacts, especially bootstrap files under `WorkDir/<source|target>/nydus_bootstrap`. This function bridges parser/remote state to filesystem-based validation.

## Risks and Test Signals
The parser selection uses `dir == "source"` rather than robust path identity, so callers must pass exact labels. It indexes `diffIDs[len(diffIDs)-1]` without an explicit empty check for non-model Nydus images. Tests cover JSON dump, OCI output, bootstrap diff mismatch, model subject errors, and successful bootstrap unpacking with monkeypatched pull.
