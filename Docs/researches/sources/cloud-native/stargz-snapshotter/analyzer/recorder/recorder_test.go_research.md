# sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder_test.go

Purpose: Validates that `ImageRecorder` maps paths to the correct image layer and handles OCI overlay semantics.

Important APIs tested: `imageRecorderFromManifest`, `ImageRecorder.Record`, `ImageRecorder.Commit`, and the emitted `recorder.Entry` JSON stream. Helper `gzipCompress` creates compressed layer inputs.

Control flow: Table cases build synthetic layer tar blobs into a local containerd content store, create a manifest descriptor list, instantiate the recorder, record requested paths, commit the output, then decode the resulting content blob and compare path/layer-index pairs in order. The tests run across accepted path prefixes (`""`, `"./"`, `"/"`, `"../"`) and both uncompressed and gzip layer media types.

State and persistence: Uses a temporary local content store and removes it after the test. Each layer and record output is committed as content-store data.

Dependencies and integration: Uses containerd local content store, testutil tar builders, OCI descriptors, gzip, and the production recorder JSON entry type.

Risks covered: Duplicate names across layers must resolve to the topmost layer. Whiteout files and opaque directory whiteouts must cause recording to fail for deleted paths. Non-regular tar entry types such as symlink, device, and fifo are indexed by name.

Test signals: Strong focused coverage for path normalization and overlay behavior. It does not cover `RecordGlob`, concurrent `Record`, or content-store error paths.
