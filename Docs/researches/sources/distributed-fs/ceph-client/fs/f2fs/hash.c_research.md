<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/hash.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/hash.c

## Purpose

`hash.c` computes F2FS directory entry name hashes. It uses the ext3-derived TEA name hash for ordinary names, but switches input strings for casefolded directories and uses fscrypt siphash for encrypted casefolded plaintext names. The resulting hash is stored in `struct f2fs_filename` and used by directory lookup and insertion code.

## Important APIs, Types, and Functions

- `TEA_transform()` is the 16-round transform that updates a two-word hash buffer from four input words using the TEA delta constant.
- `str2hashbuf()` packs up to `num * 4` filename bytes into 32-bit words with a length-derived pad value.
- `TEA_hash_name()` initializes the legacy ext hash seed, processes 16-byte chunks, and clears `F2FS_HASH_COL_BIT` in the returned value.
- `f2fs_hash_filename()` is the exported function. It expects `fname->disk_name` for all directories, and for casefolded directories it expects `usr_fname` and optionally `cf_name`.

## Control Flow and State Behavior

`.` and `..` hash to zero. For normal directories, the on-disk name bytes are passed to `TEA_hash_name()` and stored little-endian in `fname->hash`. For casefolded directories with Unicode support, the function prefers the precomputed folded name. If no folded name exists, it falls back to the user plaintext name rather than the disk name, which matters for encrypted directories because the disk name may be ciphertext. For encrypted casefolded directories, it uses `fscrypt_fname_siphash()` on the plaintext qstr and returns immediately.

## Persistence, Locking, and Integration Points

The hash value is persisted in F2FS directory entries and consumed by inline and block directory lookup/insert paths. The function integrates with Unicode casefolding, fscrypt filename handling, F2FS directory setup (`f2fs_setup_filename()`), and dentry search code. It has no internal locking and operates only on caller-prepared name buffers.

## Risks and Edge Cases

The main compatibility risk is hashing the wrong representation of a name. Casefolded encrypted directories must not hash ciphertext for fallback names, or lookups would not match plaintext user input. Invalid Unicode casefold fallback must remain stable. The collision bit is cleared from TEA hashes, so collision handling elsewhere can use that bit. The function warns if expected name pointers are absent but otherwise relies on callers to prepare `struct f2fs_filename` correctly.

## Test Signals

Tests should cover normal ASCII names, long names spanning multiple 16-byte chunks, `.` and `..`, hash stability across endian conversions, casefolded valid Unicode names, casefolded invalid Unicode fallback, encrypted plus casefolded plaintext hashing, and lookup/insert behavior under deliberate hash collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/hash.c -->
