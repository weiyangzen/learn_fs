# sources/cloud-native/soci-snapshotter/util/ioutils/multireadcloser.go

Purpose: this file combines multiple `io.ReadCloser` values into one sequential reader that closes all underlying resources.

Important API: `MultiReadCloser` stores the underlying closers and embeds an `io.Reader`. `NewMultiReadCloser` converts the closers to readers and wraps them with `io.MultiReader`. `Close` iterates all closers and returns `errors.Join` of any close failures.

Control flow: reads proceed in order through `io.MultiReader`; close is independent of read position and attempts every closer even if earlier closes fail.

State and persistence: in-memory wrapper only. Closing affects the underlying resources.

Dependencies and integration points: useful when content is assembled from multiple streams but callers need a single closeable reader.

Risks: no nil checks for input closers. `Close` can be called multiple times and will call underlying closers multiple times. There are no direct tests in this subset. The constructor uses `for i := range len(rcs)`, requiring a Go version that supports ranging over integers.

Test signals: absent here; should be tested for read order, close-all semantics, and joined errors.
