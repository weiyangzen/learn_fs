# sources/distributed-fs/ceph/src/rgw/rgw_crypt.cc

## Purpose
Implements RGW server-side encryption for PUT/POST/GET/COPY paths, including legacy AES-256-CBC, AES-256-GCM AEAD, KMS/SSE-S3/SSE-C request processing, crypto context canonicalization, object/range filters, and bucket-key management.

## Important APIs, types, and functions
`make_canonical_context()` normalizes KMS encryption context JSON with ICU NFC normalization, deterministic key ordering, and injected object ARN. `AES_256_CBC` implements 4 KiB chunked CBC with offset-derived IVs and partial-block xor handling. `AES_256_GCM` implements 4 KiB AEAD chunks, 16-byte tags, part-number/chunk-index IV layout, chunk-index AAD, accelerator fallback, random salt, HMAC-derived object keys, and per-part keys. `RGWGetObj_BlockDecrypt` maps requested plaintext ranges to encrypted ranges and decrypts cached chunks, including multipart part boundaries. `RGWPutObj_BlockEncrypt` encrypts streaming PUT data and tracks expanded encrypted offsets. `rgw_s3_prepare_encrypt()` and `rgw_s3_prepare_decrypt()` validate headers, retrieve/derive keys, set response headers, and write/read encryption attrs. `rgw_get_aead_original_size()` and `rgw_get_aead_decrypted_size()` support size accounting. `rgw_remove_sse_s3_bucket_key()` cleans bucket KEKs when safe.

## Control flow
Encryption preparation first handles SSE-C, then SSE-KMS, then SSE-S3, then default RGW auto encryption. Each branch validates required headers/config, obtains or derives a 256-bit key, chooses CBC or GCM from `rgw_crypt_sse_algorithm`, writes mode/key metadata attrs, and optionally returns a configured `BlockCrypt`. PUT data then flows through `RGWPutObj_BlockEncrypt`, which buffers to block boundaries and flushes the final partial block. Decryption preparation reads `RGW_ATTR_CRYPT_MODE`, validates request headers for SSE-C, reconstitutes KMS/SSE-S3 keys or default keys, reconstructs GCM salt and identity, and returns a decryptor. GET range fixup projects plaintext/compressed ranges to encrypted chunk reads before decryption.

## State and persistence
Persistent state is object/bucket metadata: `RGW_ATTR_CRYPT_MODE`, key id/selector/context/key MD5, salt, original size, crypt parts, prefetch alignment, and bucket encryption key id. GCM ciphertext stores an auth tag per encrypted chunk, so encrypted object size differs from plaintext size. Sensitive in-memory keys are zeroized in destructors and after use where practical.

## Dependencies and integration points
Uses OpenSSL EVP, Ceph crypto/HMAC/MD5/base64, crypto accelerator plugins, RGW KMS helpers, object manifests, range projection, SAL request state, compression filters, bucket attrs, ICU, RapidJSON, and RGW request/environment abstractions.

## Risks and test signals
This is security-critical. Risks include GCM range projection errors, wrong copy-source identity during key derivation, multipart part-number mapping, malformed or missing salt/original-size attrs, accelerator/authentication failure handling, integer overflow in expanded sizes, logging of sensitive material, and compatibility with legacy CBC attrs. Tests should cover SSE-C/KMS/SSE-S3/auto CBC and GCM, multipart non-contiguous part numbers, GET ranges across chunk and part boundaries, copy-object decrypt/re-encrypt, compression plus encryption, KMS context canonicalization, auth tag corruption, wrong key/object identity failures, bucket key create/remove races, and size accounting.
