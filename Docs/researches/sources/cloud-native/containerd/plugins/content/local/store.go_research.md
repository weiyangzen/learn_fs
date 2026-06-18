<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store.go -->
# sources/cloud-native/containerd/plugins/content/local/store.go

## Purpose
Core filesystem implementation of content.Store with digest-addressed blobs, resumable ingest transactions, optional labels, and optional fsverity integrity.

## Important APIs, Types, And Functions
LabelStore interface; store fields; NewStore/NewLabeledStore; Info, ReaderAt, Delete, Update, Walk, Status, ListStatuses, WalkStatusRefs, Writer, Abort, blobPath, ingestRoot, timestamp helpers.

## Control Flow
New store creates root and probes fsverity. Writer locks a ref, hashes ref to ingest path, resumes valid ingest by replaying data into the digester or creates ref/timestamp/total files, then returns writer. Info/Walk read blobs under blobs/<alg>/<encoded>. Status reads ingest metadata. Update delegates label mutations and adjusts atime.

## State And Persistence
Persistent layout: root/blobs/<algorithm>/<digest> for committed blobs and root/ingest/<digest(ref)>/{ref,data,startedat,updatedat,total} for active uploads. Labels are stored by optional LabelStore, not filesystem by default. ensureIngestRootOnce memoizes directory creation.

## Dependencies And Integration Points
Implements core/content.Store and integrates filters, errdefs, fsverity, digest algorithms, and writer.go commit logic. Registered by plugin/plugin.go.

## Risks And Edge Cases
In-memory locks are not cross-process. Resume rehashes entire data file and can be slow. Walk tolerates invalid digest paths by logging. Label updates are unsupported when ls is nil. Delete uses RemoveAll on blob path.

## Test Signals
store_test.go, locks_test.go, content testsuite, benchmarks, and fuzz test cover creation, writer resume, duplicate commits, walk, fsverity, labels, truncation recovery, and timestamp parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store.go -->
