<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types.go -->
## sources/control-plane/ceph-csi/pkg/util/crypto/types.go

Purpose: defines encryption mode enum parsing and stringification for public crypto utilities.

APIs: `EncryptionType` enum values are invalid, none, block, and file. `ParseEncryptionType` accepts `"block"`, `"file"`, and empty string for none; all other strings are invalid. `String` returns stable config strings, empty for none, `"INVALID"` for invalid, and `"UNKNOWN"` for unrecognized enum values.

State and persistence: stateless, but string values are configuration surface area.

Dependencies: none outside standard language.

Integration points: used by encryption configuration parsing for RBD block encryption and CephFS/file encryption (`fscrypt`) mode selection.

Risks: parser is case-sensitive and intentionally rejects combined values such as `file,block`. Comment above `EncryptionTypeFile` incorrectly says `EncryptionTypeBlock`.

Test signals: `types_test.go` covers valid, empty, invalid, combined invalid values, and round-trip string outputs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types.go -->
