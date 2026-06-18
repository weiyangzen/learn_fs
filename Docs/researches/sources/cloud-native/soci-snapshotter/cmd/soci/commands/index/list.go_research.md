## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/list.go

Purpose: implements `soci index list`, listing SOCI index artifacts with optional image ref/platform filters.

Important APIs/types/functions: filters `indexFilter`, `platformFilter`, `originalDigestFilter`, `anyMatch`, `listCommand`, `writeArtifactEntry`, and `getDuration`.

Control flow: parse flags, connect to containerd, build a filter based on ref and platforms, walk artifacts DB, sort by creation time descending, then print quiet digest list or tabular metadata. Ref filtering resolves image manifests for relevant platforms.

State and persistence: read-only on containerd image/content service and artifacts DB.

Dependencies and integration: containerd image platform resolution, SOCI image manifest descriptor helpers, artifacts DB, tabwriter.

Risks and test signals: image service is opened even for DB-only platform filtering. Image refs with missing platform manifests return explicit errors. No direct tests here.
