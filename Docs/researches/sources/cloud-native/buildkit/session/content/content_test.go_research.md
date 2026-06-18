<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/content_test.go -->
# sources/cloud-native/buildkit/session/content/content_test.go

Purpose: integration test for attachable content stores over a BuildKit session.

Important APIs, types, and functions: `TestContentAttachable` creates two local content stores, writes distinct blobs, starts a session and manager connected via `testutil.TestStream`, attaches both stores, then reads each blob through `NewCallerStore`.

Control flow and state: uses `errgroup` to run session and caller concurrently. Test data lives in temporary directories and session closes after successful reads.

Dependencies and integration: exercises `session.NewSession`, `session.NewManager`, content attachable registration, content caller proxy, containerd local store, and test stream plumbing.

Risks and test signals: covers happy-path store selection but not missing metadata, unknown store ids, write/update/delete methods, or session cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/content_test.go -->
