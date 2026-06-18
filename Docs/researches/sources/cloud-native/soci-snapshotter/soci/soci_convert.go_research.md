# sources/cloud-native/soci-snapshotter/soci/soci_convert.go

Purpose: this file converts a normal image into a SOCI-enabled OCI index. It builds SOCI v2 indexes, annotates image manifests with SOCI index digests, appends/replaces SOCI index descriptors in the top-level OCI index, writes new content, updates artifact DB references, and adds GC labels.

Important APIs and types: `ConvertOption` mutates `convertConfig`. `ConvertWithPlatforms` selects platform builds. `ConvertWithNoGarbageCollectionLabels` disables root GC labels on the converted image. Main methods are `IndexBuilder.Convert`, `buildSociIndexesv2ForPlatforms`, `newOciIndex`, `annotateImages`, `addSociIndexes`, `pushOCIObject`, and `updateSociV2ArtifactReferences`.

Control flow: `Convert` discovers supported platforms and adapts single-manifest inputs by setting target/default platform. It builds or loads an OCI index, builds SOCI v2 indexes per selected platform, rewrites relevant image manifests with `com.amazon.soci.index-digest`, adds SOCI descriptors to the OCI index, pushes the new index, updates artifact DB records to point at the rewritten manifest and new image digest, then labels all referenced manifests and optionally the root index for GC. `annotateImages` tolerates missing manifests when no SOCI index was built for that platform, enabling reduced-platform pushes.

State and persistence: converted manifests and indexes are pushed to `blobStore`; artifact DB records are mutated through `updateSociV2ArtifactReference`; containerd GC labels are written through `store.LabelGCRefContent` and `LabelGCRoot`.

Dependencies and integration points: heavily integrates containerd `images`, platforms, OCI media types, local `ociutil`, SOCI index builder, and content-store abstraction.

Risks: converting manifests changes digests and creates a new image identity. `pushOCIObject` returns descriptors without media type until callers set it. `ConvertWithNoGarbageCollectionLabels` leaves lifecycle responsibility to the caller. Missing manifests are skipped only in a specific branch; unexpected store errors abort. Artifact DB updates assume SOCI v2 descriptors carry `IndexAnnotationImageManifestDigest`.

Test signals: `soci_convert_test.go` only covers `addSociIndexes` append/no-op/replace behavior; full conversion, annotation, push, GC labels, and artifact DB updates are not covered in this subset.
