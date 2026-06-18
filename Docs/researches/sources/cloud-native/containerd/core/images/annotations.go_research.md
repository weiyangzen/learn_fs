# sources/cloud-native/containerd/core/images/annotations.go

Purpose: central constants for containerd image-related descriptor annotations.

Important constants: `AnnotationImageName` stores the containerd image name on descriptors in `index.json`. `AnnotationManifestSubject` marks descriptors that are referrers to a subject manifest and should not create a new image during import/export handling.

Control flow and state: none; constants only.

Dependencies and integration: used by image archive exporter/importer, image stores, and referrer handling to preserve names and avoid treating subject referrers as primary images.

Risks: annotation spelling is part of archive compatibility. Misusing `AnnotationManifestSubject` can hide legitimate images or create unwanted images.

Test signals: no direct tests. Archive import/export tests should assert these annotations are written and interpreted correctly.
