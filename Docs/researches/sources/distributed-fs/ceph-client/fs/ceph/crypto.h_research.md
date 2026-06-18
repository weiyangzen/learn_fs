# sources/distributed-fs/ceph-client/fs/ceph/crypto.h

## Purpose

`crypto.h` defines the CephFS fscrypt interface, wire/storage helper structures, constants for Ceph’s 4 KiB encryption block handling, encrypted filename buffers, and no-op fallbacks for builds without `CONFIG_FS_ENCRYPTION`.

## Important APIs and Types

`CEPH_FSCRYPT_BLOCK_SHIFT`, `CEPH_FSCRYPT_BLOCK_SIZE`, and `CEPH_FSCRYPT_BLOCK_MASK` define the crypto block size used by Ceph OSD I/O alignment. `struct ceph_fname` carries a directory inode, MDS/base64 name, optional raw ciphertext, lengths, and a no-copy marker. `struct ceph_fscrypt_truncate_size_header` describes encrypted truncate metadata sent to the MDS. `struct ceph_fscrypt_auth` wraps a versioned fscrypt context blob, and `ceph_fscrypt_auth_len` computes its serialized length.

When encryption is enabled, the header declares context, filename, readdir, and page crypt helpers implemented in `crypto.c`. It also defines `CEPH_NOHASH_NAME_MAX`, `ceph_fname_alloc_buffer`, `ceph_fname_free_buffer`, `ceph_fscrypt_blocks`, `ceph_fscrypt_adjust_off_and_len`, `ceph_fscrypt_pagecache_page`, and `ceph_fscrypt_page_offset`.

When encryption is disabled, static inline fallbacks reject encrypted parents with `-EOPNOTSUPP` where necessary, pass filenames through unchanged, leave offsets untouched, return success for crypt operations, and map page helpers to the original page.

## Control Flow

The compile-time branch keeps callsites simple. Enabled builds route operations to fscrypt-aware helpers. Disabled builds still allow unencrypted CephFS to compile and run, but attempts to create children under encrypted directories fail early from `ceph_fscrypt_prepare_context`.

The key runtime inline is `ceph_fscrypt_adjust_off_and_len`: encrypted reads expand the requested OSD range to full Ceph fscrypt blocks and align the offset downward. `ceph_fscrypt_blocks` computes how many encryption blocks overlap a byte range. `ceph_fscrypt_pagecache_page` and `ceph_fscrypt_page_offset` normalize fscrypt bounce pages back to their original page-cache page for accounting and writeback completion.

## State and Persistence Behavior

The header itself stores no state. It defines the serialized auth and truncate structures that are persisted through MDS requests/cap messages and the helpers that decide how much encrypted object data must be read or written. In disabled builds, no fscrypt state is persisted by these helpers.

## Dependencies and Integration Points

It depends on kernel fscrypt, base64, SHA-256, inode/page types, and Ceph forward declarations. `addr.c` uses the block alignment and page normalization helpers. `crypto.c` implements the declared operations. `caps.c` uses `struct ceph_fscrypt_auth` and `CEPH_FSCRYPT_BLOCK_SIZE` when encoding cap messages for encrypted inodes.

## Risks and Edge Cases

The block size must not exceed `PAGE_SIZE`, enforced by `BUILD_BUG_ON` in `ceph_fscrypt_blocks`. Enabled and disabled branches must keep matching signatures. Offset expansion changes OSD I/O lengths, so callers must later copy only the originally requested bytes and handle tails. Filename buffer allocation only occurs for encrypted parents, so callers must pair allocation/free with the same parent encryption state.

## Test Signals

Build coverage should include encryption enabled and disabled. Runtime tests should check encrypted read alignment, page/bounce-page offset accounting, fallback `-EOPNOTSUPP` for encrypted directories without fscrypt support, long filename allocation/free, and cap-message auth length calculations.
