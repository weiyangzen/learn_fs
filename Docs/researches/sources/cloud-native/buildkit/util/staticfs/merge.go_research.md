<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge.go -->
# sources/cloud-native/buildkit/util/staticfs/merge.go

Purpose: overlays two `fsutil.FS` instances with upper filesystem entries taking precedence over lower entries during walk and open.

Important APIs and types: `MergeFS`, `NewMergeFS`, `record`, `MergeFS.Walk`, and `MergeFS.Open`.

Control flow: `Walk` starts lower and upper walks concurrently, streams sorted records through channels, and merges them by path key. When the same key exists in both, upper is emitted and lower is skipped. `Open` tries upper first, falls back to lower only on not-exist errors.

State and persistence: no persistent state beyond references to lower/upper filesystems. Walk channels buffer records during traversal.

Dependencies and integration: implements `fsutil.FS`, uses `errgroup`, Go `io/fs`, and `staticfs` path-key helpers. Useful for layering generated/static filesystem inputs.

Risks: merge correctness assumes both underlying walks emit paths in sorted order by the same key function. A callback error stops the merge goroutine and propagates through errgroup.

Test signals: `merge_test.go` covers upper precedence, lower fallback, sorted walk, nested merge, and not-exist fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge.go -->
