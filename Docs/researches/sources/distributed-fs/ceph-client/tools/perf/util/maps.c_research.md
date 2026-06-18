# sources/distributed-fs/ceph-client/tools/perf/util/maps.c

## Purpose

`maps.c` implements a refcounted, lock-protected collection of `struct map` objects for a machine or thread. It supports insertion, removal, lazy sorting, address and name lookup, overlap repair, map copying, kernel-map merging, unwinder state, and debug printing.

## Important APIs, Types, and Functions

The private `DECLARE_RC_STRUCT(maps)` stores an rwsem, arrays sorted by address and optionally by DSO name, parent machine pointer, unwind/libdw state, refcount, allocation counts, last name-search index, sorted flags, and `ends_broken`. Public APIs include `maps__new()`, `maps__get()`, `maps__put()`, `maps__insert()`, `maps__remove()`, `maps__remove_maps()`, `maps__for_each_map()`, `maps__find()`, `maps__find_by_name()`, `maps__find_symbol()`, `maps__find_symbol_by_name()`, `maps__find_ams()`, `maps__fixup_overlap_and_insert()`, `maps__copy_from()`, `maps__merge_in()`, `maps__fixup_end()`, and `maps__load_first()`.

## Control Flow

Insertions append maps, grow arrays geometrically, take references, and update sorted flags. Sorting by address or name happens lazily under a write lock; readers loop until sorted state is available. Address lookup uses binary search against sorted ranges; name lookup first checks the last-hit index, then binary-searches the name array, and falls back to linear scan if allocation for the name array fails. Overlap repair sorts by address, finds the first map ending after the new map starts, then removes, replaces, shortens, or splits existing maps so the new range fits. `maps__merge_in()` rebuilds the array when merging a map into overlapping kernel maps.

## State and Persistence Behavior

The collection owns references to maps in `maps_by_address` and, when allocated, additional references in `maps_by_name`. Removal and teardown put both references. Libunwind and libdw address-space state is stored in the maps object and invalidated on removal. `ends_broken` permits temporary construction states where map ends are missing or unordered until `maps__fixup_end()` repairs them.

## Dependencies and Integration Points

It depends on map, DSO, machine, thread, rwsem, unwind, libdw, debug, and UI globals. Thread maps, machine kernel maps, fork map cloning, mmap event handling, callchain/unwind access, and symbol resolution all depend on this file.

## Risks and Edge Cases

The locking note documents a race between sorting and later inserts; code retries but assumes inserts are rare. Callback iteration can be unsafe if callbacks insert maps, so the loop reloads array pointers each time and may skip or repeat entries. Name-array reallocation failure disables and rebuilds the index later. Overlap repair must preserve pgoff when splitting trailing ranges. Refcount balance is subtle because maps may live in two arrays.

## Test Signals

Tests should cover sorted and unsorted insertions, address/name lookup, last-name cache hits, name-array allocation failure fallback, removal from both arrays, overlap cases where a new map covers, splits, trims before, or trims after an existing map, map copying from parent threads, `maps__merge_in()` with overlapping kernel maps, `maps__fixup_end()` for missing ends, and libdw invalidation on removals.
