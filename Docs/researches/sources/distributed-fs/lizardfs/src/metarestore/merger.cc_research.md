# sources/distributed-fs/lizardfs/src/metarestore/merger.cc

## Purpose
`merger.cc` merges multiple changelog streams in ascending change-id order and replays them into master restore logic. It is the replay engine used by `metarestore/main.cc`.

## Important APIs, Types, And Functions
- Internal `hentry` stores an open changelog file, filename, line buffer, parse pointer, and next record id.
- `merger_start(const std::vector<std::string>&, uint64_t)` opens files, reads the first usable record from each, and initializes a min-heap ordered by `nextid`.
- `merger_loop()` repeatedly restores the smallest next record and advances/removes heap entries until all logs are exhausted or restore fails.
- `merger_nextentry`, `merger_heap_sort_up`, `merger_heap_sort_down`, `merger_delete_entry`, and `merger_new_entry` are internal heap and file-lifetime helpers.

## Control Flow
`merger_start` allocates a heap sized to the file list, opens each changelog, reads its first line, drops entries with invalid first ids, and heapifies incrementally. `merger_loop` takes `heap[0]`, calls `restore(filename,nextid,ptr,RestoreRigor::kIgnoreParseErrors)`, advances that file with `merger_nextentry`, removes exhausted or invalid files, and restores heap order after each step.

`merger_nextentry` parses the decimal id at the beginning of each line with `strtoull`, retaining the rest of the line in `ptr` for restore. It accepts only monotonically increasing ids with a gap less than `maxidhole`; otherwise it logs garbage at EOF and marks the file exhausted.

## State And Persistence
The module uses static global `heap`, `heapsize`, and `maxidhole`; it is single-session and not reentrant. It owns file descriptors, duplicated filename strings, and line buffers. It does not persist data directly; persistence happens after replay in `main.cc`.

## Dependencies And Integration Points
It integrates with `master/restore.h` for record application and LizardFS status/error codes. Syslog is used for invalid changelog or file-open messages. `BSIZE` fixes the maximum line read buffer at 200000 bytes.

## Risks
- `maxidhole` is assigned after initial `merger_nextentry` calls in `merger_start`; because initial `nextid` is `0`, first lines are accepted, but the ordering is fragile.
- Static global state means concurrent merger runs in one process would collide.
- `malloc(sizeof(hentry)*filenames.size())` with an empty vector may return null on some implementations; `main.cc` calls it with empty lists in some modes, although `merger_loop` then does no work.
- Changelog lines longer than `BSIZE-1` are split by `fgets`, likely causing parse errors or false garbage detection.
- The code frees C allocations manually and assumes all heap slots have been initialized by `merger_new_entry` before deletion.

## Test Signals
Targeted tests should feed multiple changelog files with interleaved ids, duplicate/non-monotonic ids, large id gaps, unreadable files, empty files, and restore failure propagation. A fake `restore` hook would make ordering assertions straightforward.
