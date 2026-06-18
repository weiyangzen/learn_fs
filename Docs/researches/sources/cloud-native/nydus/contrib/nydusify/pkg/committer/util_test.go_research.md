# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/util_test.go

Purpose: verifies `Counter` write accounting.

Important APIs and flow: `TestCounterWriteAndSize` checks initial zero size, writes two byte slices, verifies returned lengths, nil errors, and cumulative size.

State and persistence: pure in-memory.

Dependencies and integration: protects blob-size logging used by committer pack paths.

Risks and test signals: covers sequential writes. It does not stress concurrent writes, though the implementation uses atomics.
