## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/info.go

Purpose: implements `soci ztoc info`, emitting JSON metadata for a zTOC.

Important APIs/types/functions: `Info`, `FileInfo`, and `infoCommand`.

Control flow: parse digest, open artifacts DB, reject SOCI index digests, open selected content store, fetch and unmarshal zTOC, open gzip index info, clear checkpoints, compute per-file span ranges and multi-span count, marshal indented JSON, and print.

State and persistence: read-only against DB/store.

Dependencies and integration: SOCI artifact metadata, zTOC compression metadata, store abstraction.

Risks and test signals: full file metadata is printed, which can be very large or sensitive. No direct tests here.
