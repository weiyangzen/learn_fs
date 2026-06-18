<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go

## Purpose
Defines the hard-link ID marker and generator used by filer entries that share chunk/attribute state.

## Important APIs and Types
`HARD_LINK_MARKER` is byte `0x01`. `HardLinkId` is a byte slice documented as 16 random bytes plus marker byte. `NewHardLinkId` returns random bytes with the marker appended.

## Control Flow and State
The generator has no inputs. It uses `util.RandomBytes(16)` and appends the marker.

## Persistence Behavior
The ID is persisted in entry metadata and used as a KV key by `filerstore_hardlink.go` to store shared attributes and chunks.

## Dependencies and Integration Points
Integrated with `FilerStoreWrapper` hard-link read/write/delete and inode derivation in `filer_inode.go`.

## Risks
The type is mutable because it is a byte slice. Callers should avoid modifying IDs after persistence. Random collision risk is negligible but not checked here.

## Test Signals
Hard-link inode sharing is covered in `filer_inode_test.go`; hard-link KV counter behavior is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_hardlink.go -->
