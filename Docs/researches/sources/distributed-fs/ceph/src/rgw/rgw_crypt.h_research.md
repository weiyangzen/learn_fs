# sources/distributed-fs/ceph/src/rgw/rgw_crypt.h

## Purpose
Declares RGW encryption interfaces, AEAD geometry helpers, encryption/decryption filters, S3 preparation functions, and small attr helpers.

## Important APIs, types, and functions
`BlockCrypt` is the polymorphic block cipher interface with plaintext and encrypted block sizes, `encrypt()`, `decrypt()`, and optional part-number selection. Constants define AES-256 key size and GCM salt/IV/tag/chunk sizes. `is_aead_mode()`, `is_cbc_mode()`, and AEAD size/offset helpers define shared geometry. `RGWGetObj_BlockDecrypt` is a GET filter that fixes ranges, decrypts data, handles multipart part lengths/numbers, and exposes plaintext size conversion. `RGWPutObj_BlockEncrypt` is a PUT data processor. `rgw_s3_prepare_encrypt()` and `rgw_s3_prepare_decrypt()` are the main S3 integration APIs.

## Control flow
Operation handlers call prepare functions to populate attrs and obtain a `BlockCrypt`, then insert PUT/GET filters around the normal object data pipeline. Helpers keep range and content-length logic consistent for size-expanding AEAD modes.

## State and persistence
The header defines attr-facing size behavior but not the attrs themselves. It captures decrypt filter state for offsets, caches, multipart lengths, part numbers, encrypted total size, and compression presence.

## Dependencies and integration points
Depends on RGW op/rest/put object APIs, SAL data processors, Ceph yields, and Ceph `bufferlist`. It is consumed by S3 operations, copy paths, object writes, and object reads.

## Risks and test signals
Incorrect geometry helpers will affect range reads, object size, bucket index, quotas, and cls prefetch. Tests should exercise all AEAD helper edge cases, zero-sized objects, malformed encrypted remainders, compression interaction, multipart fallback behavior, and `BlockCrypt` implementations with equal and expanded block sizes.
