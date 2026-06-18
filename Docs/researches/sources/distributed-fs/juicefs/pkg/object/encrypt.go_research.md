# sources/distributed-fs/juicefs/pkg/object/encrypt.go


Purpose: implements whole-object encryption wrappers and key parsing/encryption primitives for JuiceFS object storage.

Important APIs and flow: `ParsePrivateKeyFromPem` handles RSA PKCS#1, PKCS#8, encrypted PEM, and SM2 PKCS#8 keys, returning `ErrKeyNeedPasswd` when encrypted keys lack passphrases. `NewRSAEncryptor` uses RSA-OAEP/SHA256; `NewSM2Encryptor` uses SM2 ASN.1 encryption; `NewKeyEncryptor` dispatches by private key type. `NewDataEncryptor` creates AEAD data encryptors for AES-256-GCM, ChaCha20-Poly1305, or SM4-GCM. `dataEncryptor.Encrypt` generates a random data key and nonce, wraps the key, and stores a compact header; `Decrypt` reverses it. `NewEncrypted` wraps any `ObjectStorage`, encrypting complete objects on `Put` and decrypting complete objects before slicing on `Get`.

State and persistence: encrypted object bytes include wrapped data key, nonce, and AEAD ciphertext. The wrapper keeps the key encryptor in memory and delegates persistent storage to the underlying backend.

Dependencies and integration: integrates with RSA, GM/T SM2/SM4/SM3 libraries, `SupportTier`, and `ObjectStorage`. `Shutdown` unwraps encrypted stores.

Risks: whole-object mode reads entire plaintext/ciphertext into memory and cannot perform efficient range reads. Unsupported private-key types panic in `NewKeyEncryptor`. Typoed error text `"decryt key"` is externally visible. `ExportRsaPrivateKeyToPem` contains an unused error check after ignored return.

Test signals: `encrypt_test.go` covers key parsing, RSA/SM2 operations, AEAD round trips, overhead bounds, benchmarks, and encrypted mem-store behavior.
