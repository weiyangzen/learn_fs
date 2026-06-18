<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go

Purpose: tests dm-verity and Kata virtual volume validation/parsing behavior.

Important tests: `TestDmVerityInfoValidation` enumerates invalid hash types, sizes, block counts, offsets, and a valid SHA-256 case. `TestDirectAssignedVolumeValidation`, `TestImagePullVolumeValidation`, and `TestNydusImageVolumeValidation` cover simple metadata/config validators. `TestKataVirtualVolumeValidation` checks direct-block volume validity. `TestParseDmVerityInfo` tests valid JSON and invalid JSON. `TestParseKataVirtualVolume` tests base64 encode/decode, invalid JSON, invalid base64, and missing required fields.

Control flow and state: pure tests over JSON/base64 structs; no mounts or snapshotter state.

Dependencies/integration: uses testify assertions.

Risks and test signals: comments say non-power-of-two sizes are invalid, but production range-only validation means `3000` passes if in range; this mismatch is a test/spec signal to inspect. Mount option construction paths are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go -->
