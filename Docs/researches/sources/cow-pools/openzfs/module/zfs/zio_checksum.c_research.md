# File Research: sources/cow-pools/openzfs/module/zfs/zio_checksum.c

Read coverage: complete file, 609 lines.

Purpose: checksum algorithm registry and checksum compute/verify implementation for ZIO and SPA blocks.

Main responsibilities:
- Defines `zio_checksum_table[]`, mapping checksum IDs to native/byteswap ABD functions, optional context-template init/free functions, flags, and stable on-disk names.
- Provides Fletcher-2 and Fletcher-4 ABD implementations, plus references to SHA-256, SHA-512, Skein, Edon-R, and BLAKE3 functions.
- Maps checksum algorithms to feature flags with `zio_checksum_to_feature()`.
- Selects inherited/on/dedup checksum settings with `zio_checksum_select()` and `zio_checksum_dedup_select()`.

Checksum table behavior:
- `inherit` and `on` are policy values, not executable checksum functions.
- `off` returns zero checksum.
- `label` and `gang_header` use SHA-256 and embedded checksum fields.
- `zilog` and `zilog2` use Fletcher-2 embedded forms.
- `sha256`, `sha512`, `skein`, and `blake3` are metadata/dedup/nopwrite-capable.
- Salted algorithms use per-SPA checksum templates initialized lazily from the pool checksum salt.

Embedded checksum logic:
- `zio_checksum_compute()` handles embedded checksums by temporarily writing verifier data into `zio_eck_t`, computing over the ABD, then writing the resulting checksum back into the embedded checksum field.
- Gang headers use a verifier derived from DVA identity and physical birth.
- Labels use a verifier derived from label offset.
- ZILOG2 sizes the checksum range from `zil_chain_t.zc_nused`.

Encryption interaction:
- `zio_checksum_handle_crypt()` preserves MAC words in encrypted block checksums.
- For non-strong checksums it XORs entropy from high words into low words before storing MAC-related words.
- Verification truncates encrypted non-objset checksums to compare only the checksum portion; MAC validation happens through decryption/authentication.

Verification:
- `zio_checksum_error_impl()` validates algorithm IDs, initializes templates, extracts expected embedded or BP checksum, handles byteswapped embedded records, recomputes the actual checksum, restores overwritten verifier bytes, fills `zio_bad_cksum_t`, and returns `ECKSUM` on mismatch.
- `zio_checksum_error()` selects checksum type from BP or physical checksum property, adjusts gang header size for dynamic gang headers, retries old gang size for compatibility, updates the in-core gang node size if old-style verification succeeds, and applies checksum fault injection after a clean verify.

Lifecycle:
- `zio_checksum_templates_free()` frees any per-SPA checksum context templates before SPA deallocation.

Key dependencies:
- Called by `zio.c` checksum generate/verify stages.
- Uses ABD iteration, Fletcher helpers, algorithm-specific checksum providers, SPA feature/template state, ZIL structures, and ZIO fault injection.
