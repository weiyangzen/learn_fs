<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/diff.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/diff.go

- Purpose: Implements diff generation, change listing, applying diffs, and diff-size commands.
- Important functions/types: `changes`, `diff`, `fileFetcher`, `sendFileParts`, `GetBlobAt`, `applyDiffUsingStagingDirectory`, `applyDiff`, and `diffSize`.
- Control flow: Generate archive diffs between layers, list filesystem changes, optionally stream file chunks through a staging directory, apply tar streams to layers, and compute diff sizes.
- State and persistence: `applyDiff*` mutates layers; diff/read operations may mount or stream layer content.
- Dependencies and integration: Uses containers/image chunked interfaces, storage Diff/ApplyDiff APIs, and file streaming channels.
- Risks: Tar stream handling is sensitive to untrusted input; staging directory cleanup and chunk errors must be handled to avoid leaks/corruption.
- Test signals: Diff/apply round-trip integration tests and change-list expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/diff.go -->
