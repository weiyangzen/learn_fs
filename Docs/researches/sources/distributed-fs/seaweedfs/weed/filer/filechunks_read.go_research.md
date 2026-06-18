<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go

## Purpose
Computes visible, non-overlapping file intervals from a possibly overlapping list of resolved chunks. This is the sweep-line engine used by `NonOverlappingVisibleIntervals` and therefore by reads, compaction, and chunk deletion.

## Important APIs and Types
`readResolvedChunks` converts chunks into start/end `Point`s and returns `IntervalList[*VisibleInterval]`. `addToVisibles` and `appendVisibleInterfal` append visible ranges. `Point` carries coordinate `x`, timestamp `ts`, chunk pointer, and start/end flag.

## Control Flow and State
The algorithm creates two points for each chunk, sorts by offset, timestamp, and start/end ordering, then maintains a `container/list` ordered by timestamp. The tail is the current visible chunk. When a higher timestamp chunk starts, or the current highest timestamp chunk ends, the code emits a visible interval from `prevX` to the current point.

## Persistence Behavior
No persistence. It works only with resolved chunks; manifest chunks are unexpected and printed as a warning-like message.

## Dependencies and Integration Points
Uses Go `slices.SortFunc`, `container/list`, `filer_pb.FileChunk`, and package `IntervalList`. Called indirectly by read planners and compaction. It assumes manifest resolution has already expanded manifest chunks.

## Risks
The code uses `int(a.x - b.x)` and similar timestamp casts in sorting; very large differences can overflow `int` on some platforms. Equal timestamp behavior depends on insertion/removal order. The function clips chunks for overlap detection but appends original chunk offset points rather than clipped `start`/`stop` points, so correctness relies on later callers using compatible ranges; current tests cover common and random cases.

## Test Signals
`filechunks_read_test.go` includes randomized byte-array verification, sequential large chunks, and actual bug layouts. `filechunks_test.go` also validates expected visible intervals for overwrite patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read.go -->
