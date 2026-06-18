# sources/cloud-native/nydus/rafs/src/mock/mock_super.rs

## Purpose
`mock_super.rs` defines a minimal in-memory `RafsSuperBlock` implementation for tests. It provides inode lookup through a hash map while leaving operations unrelated to lookup intentionally unimplemented.

## Important APIs, Types, And Functions
`MockSuperBlock` stores `HashMap<Inode, Arc<MockInode>>`. `CHUNK_SIZE` is a test constant used by `MockInode` and v5 IO allocation tests. `MockSuperBlock::new` constructs an empty map. The `RafsSuperInodes` implementation supports `get_inode` and `get_extended_inode` by map lookup and `enoent!` on misses; `get_max_ino` is unimplemented. The `RafsSuperBlock` implementation leaves `load`, `update`, `get_blob_infos`, `root_ino`, `get_chunk_info`, and `set_blob_device` unimplemented while making `destroy` a no-op.

## Control Flow
Tests insert `Arc<MockInode>` values into the map, then exercise lookup through both base and extended inode trait paths. Missing keys return `enoent!`. Any test that calls unimplemented superblock-level operations should panic.

## State And Persistence
State is limited to the in-memory inode map. There is no metadata loading, metadata update, blob table, root inode state, or persistent storage effect. `destroy` does not clear the map.

## Dependencies And Integration Points
The mock depends on `MockInode`, shared metadata traits, RAFS reader/result aliases, and storage blob types required by the trait signatures. It supports tests that need a `RafsSuperBlock` trait object but only care about inode lookup.

## Risks
This mock is deliberately partial. It cannot model max inode, root inode, blob enumeration, update/load, v6 chunk table access, or blob-device injection. Tests using it should not assume production superblock lifecycle or blob behavior is covered. The `CHUNK_SIZE` value is arbitrary and only meaningful in the mock/test context.

## Test Signals
Tests cover successful and failed inode lookups for base and extended traits, expected panics for unimplemented methods, and that `destroy` is callable. Helper code constructs a temporary reader only to invoke panic paths for `load` and `update`.
