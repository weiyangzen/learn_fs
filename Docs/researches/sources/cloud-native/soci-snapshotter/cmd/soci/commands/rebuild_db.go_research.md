## sources/cloud-native/soci-snapshotter/cmd/soci/commands/rebuild_db.go

Purpose: implements `soci rebuild-db`, synchronizing artifacts DB with local content store blobs.

Important APIs/types/functions: `RebuildDBCommand`.

Control flow: connect to containerd, open artifacts DB, open configured blob store, compute content-store blob path from store type/root, and call `artifactsDb.SyncWithLocalStore`.

State and persistence: mutates artifacts DB based on local store and containerd content.

Dependencies and integration: containerd content store, SOCI store path helpers, artifacts DB sync logic.

Risks and test signals: correctness depends on store path layout and `SyncWithLocalStore`. No direct tests here.
