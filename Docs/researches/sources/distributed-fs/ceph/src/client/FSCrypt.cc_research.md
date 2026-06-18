# sources/distributed-fs/ceph/src/client/FSCrypt.cc

## Purpose
`FSCrypt.cc` implements Linux-only fscrypt support for libcephfs: kernel-compatible filename armoring, HKDF key derivation, key store management, OpenSSL cipher setup, filename/symlink encryption, file-data block encryption/decryption, and preparation for encrypted reads.

## Important APIs, Types, and Functions
Name armoring is handled by `fscrypt_fname_armor()` and `fscrypt_fname_unarmor()` over a kernel-compatible base64 alphabet. HKDF is implemented by `fscrypt_calc_hkdf()` using HMAC-SHA512 extract/expand. `FSCryptKey::init()` derives the key identifier and stores the raw key. `FSCryptKeyStore::{create,find,invalidate}` manage master keys, users, epochs, present flags, and decrypted inode tracking. `FSCryptDenc` sets up OpenSSL EVP ciphers, derives per-file keys, and encrypts/decrypts buffers. `FSCryptFNameDenc` encrypts/decrypts filenames and symlinks, including alternate-name handling for long encrypted names. `FSCryptFDataDenc` encrypts/decrypts block-aligned file data. `FSCrypt::init_ctx()`, `get_fname_denc()`, `get_fdata_denc()`, and `prepare_data_read()` are the main facade methods.

## Control Flow
Keys are added to `FSCryptKeyStore`, which derives an identifier and either creates or refreshes a handler. An inode decodes `fscrypt_auth` into an `FSCryptContext`; callers request a name or data denc, which resolves the master key, snapshots its epoch in an optional validator, configures the OpenSSL cipher, and derives a per-file key. Filename encryption pads plaintext, encrypts, hashes overflow bytes into a short no-hash name when needed, armors the result, and may retain alternate ciphertext. Data encryption expands writes to full fscrypt blocks and encrypts each block with an IV based on block number. Data decryption walks target blocks, treats recorded or zero-detected holes as zeroes, decrypts non-hole chunks, and splices requested ranges into the output.

## State and Persistence Behavior
The key store is process-local and guarded by shared mutexes. It tracks key handler epoch changes so validators can detect stale derived ciphers. `fscrypt_auth` and `fscrypt_file` are persisted as inode metadata by higher layers/MDS; this file encodes/decodes contexts and effective encrypted size but does not persist by itself. Key invalidation may leave handlers present=false with files busy until decrypted inode tracking empties.

## Dependencies and Integration Points
It depends on Ceph crypto wrappers, OpenSSL EVP/provider APIs, fscrypt uapi definitions, `bufferlist`, Ceph logging, and `CephContext` randomness. `Inode` initializes contexts and inherited auth, while `Client` path and IO operations call name/data denc helpers.

## Risks and Edge Cases
Compatibility with Linux fscrypt format is critical: base64 alphabet, HKDF info string, padding, CTS mode, IV generation, and key identifier derivation must match kernel expectations. Stack variable-length arrays are used for padded names and symlinks. Long encrypted names require correct alternate-name storage or decryption cannot recover original names. Hole detection uses both supplied hole segments and zero checks. `FSCryptKeyHandler::reset()` assumes an existing key before zeroing; invalidation paths must avoid null dereferences. OpenSSL cipher fetch return values and provider availability are operational risks.

## Test Signals
Round-trip filename, long filename alternate-name, symlink, and file-data encryption/decryption against kernel fscrypt vectors. Test key add/remove with multiple users, busy-file invalidation flags, stale key validator behavior, sparse encrypted reads, partial-block writes, unsupported policy/cipher modes, missing key behavior, and provider failures.
