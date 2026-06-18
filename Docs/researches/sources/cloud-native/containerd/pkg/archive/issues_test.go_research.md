<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/issues_test.go -->
# sources/cloud-native/containerd/pkg/archive/issues_test.go

Purpose: regression test for reading tar archives emitted by old Go/containerd combinations using prefix headers, preserving backward compatibility for stored layers.

Important APIs and functions: `TestPrefixHeaderReadable` constructs a known gzipped tar byte sequence, decompresses it with `compression.DecompressStream`, applies it with `Apply(..., WithNoSameOwner())`, and verifies the expected long path exists.

Control flow and state: the test requires root, creates a temp extraction root, streams a static gzip payload into the archive apply path, and checks `os.Lstat` on a path derived from a long prefix/name split.

Dependencies and integration: integrates `pkg/archive/compression` with the core tar `Apply` flow and the test utility root guard. It indirectly verifies `archive/tar` compatibility with historic prefix encoding.

Risks and test signals: the static fixture is small but critical because failures would mean older content in registries or content stores can no longer be unpacked. `WithNoSameOwner` narrows the test to format readability rather than UID/GID preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/issues_test.go -->
