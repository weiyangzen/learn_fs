# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader_test.go

Purpose: tests remote resolver/fetcher/pusher wrappers, reader adapters, plain HTTP toggling, request references, and push behavior.

Important fixtures/APIs: `MockResolver`, `mockReadSeekCloeser`, `readSeekCloser`, `readerAt.ReadAt`, `Remote.ReadSeekCloser`, `Remote.Resolve`, `Remote.Pull`, `Remote.ReaderAt`, `Remote.Push`, `MaybeWithHTTP`, `WithHTTP`, `namedReference`, `requestRef`, and `FromFetcher`.

Control flow and state: tests create remotes with mock resolver factories, assert refs passed to resolver methods, fetch in-memory content, verify seeking reads, reject non-seekable readers, toggle HTTP when error strings contain the registry host, handle already-exists pushes as success, and ensure content writers commit on successful push.

Dependencies and integration points: containerd remotes/content interfaces, errdefs, digest, OCI descriptors, and testify.

Risks and test signals: coverage is comprehensive for wrapper mechanics but not for real registry auth/token expiry behavior. The typo `mockReadSeekCloeser` is test-local only.
