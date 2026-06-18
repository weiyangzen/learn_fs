## sources/cloud-native/buildkit/util/gitutil/gitsign/gitsign.go

Purpose: verifies signatures extracted from parsed Git objects, supporting both OpenPGP and SSH signature formats.

Important APIs/types: `Signature{PGPSignature,SSHSignature}`, `VerifySignature(obj,pubKeyData,policy)`, `ParseSignature`, `parseSignatureBlock`, plus private PGP/SSH verification helpers.

Control flow: `VerifySignature` requires `obj.Signature`, parses it, dispatches to PGP verification over `obj.SignedData` using `pgpsign.VerifyArmoredDetachedSignature`, or SSH verification using `sshsig`. SSH verification enforces version 1, SHA-256/SHA-512 hash, namespace `git`, parses authorized-key public data, and verifies over signed data. `ParseSignature` detects PEM armor headers.

State/persistence: stateless. Dependencies: ProtonMail OpenPGP packet types, `hiddeco/sshsig`, BuildKit `gitobject` and `pgpsign`, `x/crypto/ssh`.

Integration points: combines `gitobject.Parse` output with key material from trust policy/source configuration. Risks: no local tests; unsupported SSH hash/namespace rejection is intentional but may fail future Git signature variants; PGP policy behavior is delegated to `pgpsign`.
