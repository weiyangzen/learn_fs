## sources/cloud-native/stargz-snapshotter/fs/layer/testutil.go

Purpose: provides the comprehensive shared test suite for `fs/layer`, exercising prefetch, file reads, FUSE node behavior, overlay semantics, state files, passthrough settings, compression variants, and cache behavior.

Important APIs/types/functions: `TestSuiteLayer` runs tests for default and three passthrough configurations. `testPrefetch` builds sample eStargz blobs and validates blob cache calls, landmark-selected prefetch sizes, and cached uncompressed reads. `sampleBlob` tracks read/cache calls and duplicate regions. `testNodeRead` validates file `Read` across offsets, request sizes, chunk positions, and file sizes. `makeNodeReader` constructs a root node and opens a test file. `testNodes` and `testNodesWithOpaque` validate whiteouts, opaque dirs, landmarks, state files, special modes, symlink sizes, multi-file chunks, directory dots, xattrs, and cache hits. Numerous check helpers traverse go-fuse nodes and assert attrs/content.

Control flow: tests build eStargz blobs through `util/testutil.BuildEStargz` with gzip, zstd, and external-TOC gzip compression. Metadata readers are created from the supplied `metadata.Store`, readers are verified by TOC digest, root nodes are initialized with `fusefs.NewNodeFS`, and checks interact through FUSE-like methods (`Lookup`, `Readdir`, `Open`, `Read`, `Getattr`, xattr calls). Prefetch tests call `layer.Prefetch`, inspect remote cache arguments, then read expected files to prove no remote blob reads occur.

State and persistence: all data is in memory: sample blobs, memory caches, called offsets, test state file JSON, and synthetic node trees. The test creates no actual mountpoints. `calledReaderAt` records lower-level reads to distinguish cache hits from misses.

Dependencies and integration points: imports `estargz`, `fs/reader`, `remote`, `metadata`, go-fuse, util test tar builders, gzip/zstd compression helpers, and Linux mode/device packages. It is invoked by `layer_test.go` with the memory metadata backend.

Risks: the suite is broad but synthetic: it bypasses real registry/network behavior, real FUSE kernel mounts, disk directory cache behavior, and resolver TTL eviction. Random data supports compression-size assumptions that are likely but not mathematically guaranteed. Some passthrough scenarios only verify functional reads, not OS-level passthrough performance.

Test signals: very high signal for layer-to-node correctness, cache/preread behavior, overlay translation, and prefetch policy. Lower signal for remote resolver lifecycle and production mount/unmount interactions.
