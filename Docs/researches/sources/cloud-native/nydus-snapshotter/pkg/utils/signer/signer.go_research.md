<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go

Purpose: verifies RSA/SHA-256 signatures over streamed input.

Important APIs/types: `Signer`, `New(publicKey []byte)`, and `Verify(input io.Reader, signature []byte)`. `New` PEM-decodes a PKCS#1 RSA public key and stores it. `Verify` streams input through SHA-256 and calls `rsa.VerifyPKCS1v15`.

Control flow and state: signer state is only the parsed public key. Verification reads the entire input stream into the hash, so callers must provide a fresh reader positioned at the beginning.

Dependencies/integration: standard crypto/x509/pem/rsa packages. It likely supports image signature verification through higher-level `signature` code.

Risks and test signals: `New` does not check for a nil PEM block before `block.Bytes`, so invalid non-PEM input can panic. It expects PKCS#1 public keys, not PKIX `BEGIN PUBLIC KEY` keys. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go -->
