## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/rm.go

Purpose: implements `soci index remove/rm`, deleting index metadata and content by digest or by image ref.

Important APIs/types/functions: `rmCommand` and `removeArtifactsAndContent`.

Control flow: reject simultaneous digest args and `--ref`, open configured content store and artifacts DB, then either remove explicit digest args or look up entries associated with the image target digest and remove each artifact plus content blob.

State and persistence: mutates artifacts DB and selected content store; may connect to containerd to resolve image refs.

Dependencies and integration: SOCI artifacts DB, SOCI store abstraction, containerd image service, digest parsing.

Risks and test signals: `RemoveArtifactEntryByIndexDigest` runs before digest parsing/content deletion, so later failures may leave partial state. No direct tests here.
