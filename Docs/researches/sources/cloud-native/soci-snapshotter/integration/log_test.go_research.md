# sources/cloud-native/soci-snapshotter/integration/log_test.go

Purpose: asserts snapshotter logs do not leak sensitive information across basic and parallel pull modes.

Important APIs and flow: `TestSnapshotterDoesNotLogSensitiveInformation` runs image pulls under default lazy pull, default parallel pull, unbounded parallel pull/unpack, and discard-unpacked-layers configurations. It attaches `sensitiveInfoMonitor` to snapshotter logs while copying and pulling an image. `sensitivePatterns` includes generic credential/token terms, AWS access-key patterns, private key/certificate markers, OAuth/bearer/basic auth strings, and common sensitive environment wording.

State and persistence: creates local registry images and starts snapshotter/containerd with monitored logs. It does not inspect persisted content beyond the pull operation.

Dependencies and integration: integrates log monitoring helpers, snapshotter config options, registry mirror helpers, and both SOCI and parallel pull modes.

Risks and test signals: useful regression signal for accidental secret logging, but broad regexes can false-positive on benign log text. The test waits briefly for log flushes and depends on monitored operations producing representative resolver/auth logs.
