<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/delete.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/delete.go

- Purpose: Implements deletion commands for layers, images, containers, and a generic delete dispatcher.
- Important functions/types: `deleteThing`, `deleteLayer`, `deletedImage`, `deleteImage`, and `deleteContainer`.
- Control flow: Resolve the requested object, call the matching store delete API, optionally force image deletion/testing behavior, and report deleted IDs/layers.
- State and persistence: Removes metadata records, big data directories, layers, images, and containers from storage.
- Dependencies and integration: Uses storage deletion APIs and command aliases.
- Risks: Destructive command; image deletion can cascade layer deletion; generic dispatch can surprise users if an ID matches multiple namespaces.
- Test signals: CLI delete tests and subsequent `exists`/list commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/delete.go -->
