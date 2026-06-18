<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go -->
## sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go

Purpose: unit test for encryption type parsing and string output.

Coverage: invalid examples `wat?`, `both`, `file,block`, and `block,file`; valid block/file; empty string as none; and `ParseEncryptionType(s).String() == s` for supported string values.

Dependencies: `testify/require`.

Integration: protects config parsing from accidentally accepting ambiguous combined encryption modes.

Risks and gaps: no direct assertions for `EncryptionTypeInvalid.String()` or unknown enum `String()` branch. No case-insensitivity tests, implying exact lowercase strings are the contract.

Test signal quality: good for accepted config surface.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go -->
