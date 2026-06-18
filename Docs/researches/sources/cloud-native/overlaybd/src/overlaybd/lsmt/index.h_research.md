# sources/cloud-native/overlaybd/src/overlaybd/lsmt/index.h

## Purpose
Declares the LSMT segment mapping model and abstract memory-index interfaces used by OverlayBD layer files. The header defines the public contract for building, querying, merging, compressing, and combining logical-to-physical sector mappings.

## Important APIs and Types
`Segment` stores logical offset and length in sector units. `SegmentMapping` extends it with mapped offset, zeroed marker, and layer tag. `RemoteMapping` describes externally backed remote data ranges. `IMemoryIndex`, `IMemoryIndex0`, and `IComboIndex` define read-only, writable, and combined index operations. Exported C factories create writable/read-only/combo indexes and merge or compress mapping arrays. `foreach_segments` emits zero/hole callbacks for gaps and data callbacks for mapped ranges.

## Control Flow
Callers construct an index from sorted mappings or start with `create_memory_index0`, insert mappings, then query by `lookup` or `foreach_segments`. `foreach_segments` repeatedly calls `lookup` in bounded batches of 16, invokes the zero callback for holes or zeroed mappings, invokes the data callback for real mappings, and advances the requested segment until fully covered.

## State and Persistence
The header defines compact packed mapping records. Offset and length bit widths impose the persistent representable range for serialized LSMT indexes: 50-bit logical offsets, 14-bit lengths, and 55-bit mapped offsets.

## Dependencies and Integration Points
Integrated by LSMT file implementations, tests, tar/EROFS remote-data import, and any code that needs to present OverlayBD layer contents as a file. Uses Photon filesystem types indirectly through implementation files.

## Risks
All APIs assume sector-granular offsets and lengths. Misordered or overlapping read-only mappings break lookup semantics. Bit-field packing is ABI-sensitive, so persisted index compatibility depends on compiler/platform layout assumptions.

## Test Signals
Tests should assert structure sizes/layout expectations, lookup of gaps and trimmed edges, max-length splitting behavior, remote mapping propagation, and callback order from `foreach_segments`.
