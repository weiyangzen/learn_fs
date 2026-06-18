# sources/cloud-native/soci-snapshotter/fs/layer/util_test.go

Purpose: provides shared test fixtures and assertions for layer FUSE node behavior, including span-backed reads, whiteouts, opaque directories, mode bits, state files, and statfs reporting.

Important APIs and flow: `testNodeRead` enumerates read sizes, offsets, base spans, and file sizes, builds a node reader with synthetic ztoc data, reads through a FUSE file handle, and compares bytes. `makeNodeReader`, `makeFile`, `getRootNode`, and `getRootNodeWithStatfsBase` construct real metadata readers, span managers, `reader.Reader`, and layer nodes around fake blob state. `testExistenceWithOpaque` checks whiteout translation, hidden whiteout source entries, opaque xattr variants, preserved xattrs, state directory lookup, suid/sgid/sticky mode conversion, and symlink size. Assertion helpers walk the FUSE tree through `Lookup`/`Readdir`, read file content, inspect attrs/xattrs, and parse the state JSON. `testStatfs` verifies default zero stats and real backing filesystem stats.

State and persistence: uses temporary metadata stores, temporary statfs directories, synthetic gzip/tar ztoc readers, memory caches, and fake blob fetched-size state. It does not mount a real FUSE filesystem; it calls go-fuse node operations directly.

Dependencies and integration: integrates metadata stores, span manager, reader package, testutil tar builders, go-fuse node APIs, Unix statfs/device helpers, and idtools. It is the main behavioral test bed for `node.go`.

Risks and test signals: broad coverage of read and metadata semantics across multiple span sizes. It still does not exercise actual kernel FUSE mounting, concurrent node operations under real VFS pressure, or real remote blob refresh failures.
