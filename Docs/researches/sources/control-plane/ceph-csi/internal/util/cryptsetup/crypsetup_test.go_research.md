<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go -->
## sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go

**Purpose:** Unit-tests cryptsetup option recommendation, allowlist validation, LUKS status field modeling, and parsing of `cryptsetup status` output. The filename appears to contain a typo (`crypsetup_test.go`) but the package is `cryptsetup`.

**Important APIs and functions:** `TestGetRecommendation` covers invalid cipher, uncommon key sizes, unknown integrity modes, and recommended AES-XTS-random/HMAC combinations. `TestAllowedEncryptionOptions` exercises `EncryptionOptions.SetCipher`, `SetKeySize`, and `SetIntegrityMode`. `TestLuksStatus` tests status setters, integrity-mode translation, sector size, key-size subtraction, and `EncryptionOptions.Equal`. `TestParseLuksStatus` parses valid compound-mode output and malformed outputs. `setError` is a small assertion helper.

**Control flow, state, and persistence:** Tests are pure and parallel, using synthetic status strings. They do not run `cryptsetup` or touch block devices.

**Dependencies and integration points:** Depends on `testify/assert` and `require`. It protects the validation and parser logic that `crypto.go` uses to judge resize safety and report configuration quality.

**Risks and test signals:** Good signal for current recommendation maps and parser assumptions. It does not test command argument construction, temporary key files, AddKey/RemoveKey/VerifyKey behavior, timeout behavior, or all allowed ciphers and integrity modes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/cryptsetup/crypsetup_test.go -->
