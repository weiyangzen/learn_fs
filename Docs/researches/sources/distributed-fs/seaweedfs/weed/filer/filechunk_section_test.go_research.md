<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go

## Purpose
Tests garbage removal for a `FileChunkSection`, a chunk-section helper defined elsewhere in the filer package. The file is narrowly focused on verifying that a section's `chunks` slice is compacted after a set of file IDs is declared garbage.

## Important APIs and Functions
`Test_removeGarbageChunks` constructs a section from `NewFileChunkSection(0)`, populates five `filer_pb.FileChunk` values, builds a `map[string]struct{}` of garbage IDs, and calls `removeGarbageChunks`.

## Control Flow and State
The test mutates in-memory `section.chunks`. Persistence is not involved. The state transition under test is five chunks becoming two surviving chunks after garbage IDs `0`, `2`, and `4` are removed.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk` and package-local chunk-section helpers. It complements the broader chunk compaction logic in `filechunks.go` by testing section-level removal, likely used when compacting or rewriting chunk metadata.

## Risks
The assertion only checks surviving length, not the exact surviving IDs or order. A buggy implementation that removes the wrong three chunks could still pass.

## Test Signals
Positive signal for basic garbage filtering. Coverage is minimal and does not exercise empty maps, all-garbage, no-garbage, duplicate file IDs, or order preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunk_section_test.go -->
