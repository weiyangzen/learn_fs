# sources/distributed-fs/ceph-client/fs/ubifs/key.h

## Purpose

`key.h` defines UBIFS key helpers. Keys identify inode, data, directory-entry, xattr-entry, and replay-only truncation nodes in the TNC and on flash. The current simple key format uses 64 bits: inode or parent inode number in the high word, then type bits plus block number or hash bits in the low word. The helpers intentionally take `struct ubifs_info *c` so future key formats can be added without changing callers.

## Important APIs, Types, And Functions

Hash helpers are `key_mask_hash()`, `key_r5_hash()`, and `key_test_hash()`. Key constructors include `ino_key_init()`, `ino_key_init_flash()`, `lowest_ino_key()`, `highest_ino_key()`, `dent_key_init()`, `dent_key_init_hash()`, `dent_key_init_flash()`, `lowest_dent_key()`, `xent_key_init()`, `xent_key_init_flash()`, `lowest_xent_key()`, `data_key_init()`, `highest_data_key()`, `trun_key_init()`, and `invalid_key_init()`.

Accessors and transformers include `key_type()`, `key_type_flash()`, `key_inum()`, `key_inum_flash()`, `key_hash()`, `key_hash_flash()`, `key_block()`, `key_block_flash()`, `key_read()`, `key_write()`, `key_write_idx()`, `key_copy()`, `keys_cmp()`, `keys_eq()`, `is_hash_key()`, and `key_max_inode_size()`.

## Control Flow

Directory and xattr entry constructors hash the fscrypt name bytes with `c->key_hash`, assert the hash fits `UBIFS_S_KEY_HASH_MASK`, and combine it with the entry key type. Data keys combine inode number with block number and `UBIFS_DATA_KEY`. Inode keys use the inode number and an inode type discriminator. Lowest/highest helpers generate range bounds for TNC scans and removals, such as all nodes for an inode or all xattr entries under a host inode.

On-flash helpers write little-endian words and zero unused bytes up to `UBIFS_MAX_KEY_LEN`, except `key_write_idx()` leaves only the active key words because index-node storage has its own layout expectations. Flash accessors convert little-endian words back to CPU order. Comparison is lexicographic by the two 32-bit words, matching the simple-key sort order in the TNC.

## State And Persistence Behavior

Keys are persisted in nodes and index branches and are the stable lookup contract for replay, scan, GC, journal updates, and TNC operations. Hash values `0`, `1`, and `2` are reserved for directory offset semantics, so `key_mask_hash()` shifts small hash values upward. `trun_key_init()` is not an on-media key; it exists for replay logic that needs to represent truncation state in key-like form.

## Dependencies And Integration Points

The helpers are used throughout UBIFS: journal packing writes dent/data/ino/xent keys, GC sorts and validates nodes by key type and value, lprops debug scanning calls `ubifs_tnc_has_node()` with keys read from scanned nodes, directory lookup and readdir depend on hashed dent keys, xattr lookup uses xent keys, and truncation/delete paths use range keys for TNC removal.

## Risks And Edge Cases

The key format limits maximum file size via `UBIFS_S_KEY_BLOCK_BITS * UBIFS_BLOCK_SIZE`, so `key_max_inode_size()` must match the active format. Hash collisions are expected for dent/xent keys and are flagged by `is_hash_key()` so name-aware TNC logic can disambiguate. Encrypted names are not C strings, so constructors correctly use `fname_name()` and `fname_len()`. Endianness mistakes or failure to zero unused flash-key bytes would affect mount/replay compatibility.

## Test Signals

Test signals include directory hash collision workloads, encrypted filenames, xattr enumeration/removal ranges, large-file block key limits, TNC key ordering, flash/in-memory key round-trips, and use of lowest/highest range helpers in inode deletion and truncation paths.
