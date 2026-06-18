# sources/distributed-fs/juicefs/pkg/object/encrypt_test.go


Purpose: tests and benchmarks the key parsing, key encryption, data encryption, and whole-object encrypted storage code.

Important APIs and flow: `TestParsePrivateKey` covers RSA PKCS#1, encrypted RSA PKCS#8, plain SM2 PKCS#8, and SM2 encrypted with SM4/AES. `TestSM2` and `TestRSA` verify key encryptor round trips and PEM path parsing. `TestDataEncryptor` covers RSA/AES-GCM, RSA/ChaCha20, and SM2/SM4-GCM. `TestEncryptorMaxOverhead` checks `MaxOverhead` bounds for RSA key sizes and SM2. `TestEncryptedStore` wraps `mem` storage and verifies ranged decrypted reads plus corruption handling for an unencrypted empty object.

State and persistence: uses generated private keys, embedded PEM fixtures, temporary files, and in-memory object storage only.

Dependencies and integration: uses `crypto/rsa`, GM/T SM2 libraries, `NewEncrypted`, `CreateStorage`, and testify `require`. Benchmarks measure key encrypt/decrypt and 4 MiB data encrypt/decrypt.

Risks and gaps: tests do not assert cryptographic interoperability with external tools beyond parsing embedded key formats. Randomized encryption makes exact wire format assertions absent. `TestEncryptedStore` covers whole-object mode but not chunked mode.

Test signal: broad for supported key formats, AEAD algorithms, overhead calculations, and wrapper read slicing.
