<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/image.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/image.go

- Purpose: Implements per-image inspection, big-data, and directory path commands.
- Important functions: `image`, `listImageBigData`, `getImageBigData`, `wrongManifestDigest`, `getImageBigDataSize`, `getImageBigDataDigest`, `getImageDir`, `getImageRunDir`, and `setImageBigData`.
- Control flow: Resolve image, print metadata or JSON, list/get/set big data, calculate size/digest, and expose storage paths.
- State and persistence: `setImageBigData` writes persistent big-data items and updates size/digest metadata.
- Dependencies and integration: Uses digest handling and storage image APIs. The `wrongManifestDigest` helper supports legacy manifest digest behavior.
- Risks: Raw data output may be binary; setting manifest-like data affects later pulls/lookups.
- Test signals: Image create/data CLI tests and digest/size validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/image.go -->
