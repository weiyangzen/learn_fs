## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/list.go

Purpose: implements `soci ztoc list`, listing zTOC layer artifacts globally or for an image.

Important APIs/types/functions: `listCommand` with filters for zTOC digest, image ref, and quiet output.

Control flow: open artifacts DB; if no image ref, walk DB for layer entries. If image ref is supplied, connect to containerd, resolve image platforms, find SOCI index descriptors, decode each index from content store, collect SOCI layer blob descriptors, then map them back to DB entries for layer digest metadata.

State and persistence: read-only against artifacts DB and containerd content/image services.

Dependencies and integration: SOCI index decode, artifacts DB, containerd image platform resolution, content store reader.

Risks and test signals: stale DB entries missing content are skipped only during image-ref path. Digest plus image-ref mismatch returns explicit error. No direct tests here.
