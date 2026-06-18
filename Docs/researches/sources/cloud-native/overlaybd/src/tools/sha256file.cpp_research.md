# sources/cloud-native/overlaybd/src/tools/sha256file.cpp

Purpose: implements SHA256-calculating wrappers for Photon files and direct path hashing used by OverlayBD layer checksum validation.

Important APIs/types/functions: `SHA256CheckedFile` extends `SHA256File`, overriding `read`, `lseek`, `fstat`, `filesystem`, and `sha256_checksum`; factory `new_sha256_file`; utility `sha256sum`.

Control flow: wrapper initializes OpenSSL SHA256 context, forwards reads to the underlying file, updates the digest on every positive read, and finalizes after draining remaining data in `sha256_checksum`. `sha256sum` opens a path with `O_DIRECT`, stats it, reads aligned 64 KiB chunks using `pread`, updates SHA256, and returns `sha256:<hex>`.

State and persistence: no writes; state is the underlying file pointer, ownership flag, OpenSSL context, and current read position. Finalization consumes unread bytes from the wrapped file.

Dependencies/integration: used by `overlaybd-apply` to verify uncompressed tar layer checksums; depends on OpenSSL SHA APIs and Photon virtual file interfaces.

Risks: OpenSSL SHA256 APIs are deprecated in newer OpenSSL versions. `sha256_checksum` finalizes once and should not be called repeatedly. `sha256sum` uses `O_DIRECT`, which can fail on unsupported filesystems or with alignment-sensitive reads.

Test signals: cover streaming digest, ownership deletion, mismatched expected digest, small/unaligned file hashing, and repeated finalization behavior.
