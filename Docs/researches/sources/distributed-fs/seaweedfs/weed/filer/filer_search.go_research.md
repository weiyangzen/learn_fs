<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_search.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_search.go

## Purpose
Implements directory listing with pagination, prefix filtering, glob include/exclude matching, and expired-entry refill.

## Important APIs and Functions
`splitPattern` extracts the literal prefix before `*` or `?`. `ListDirectoryEntries` materializes results and has-more state. `CountDirectoryEntries` counts up to a limit. `StreamListDirectoryEntries` streams entries through callbacks. `doListPatternMatchedEntries` applies glob filters. `doListValidEntries` refills listings after expired entries are skipped/deleted.

## Control Flow and State
Limits are capped to `math.MaxInt32 - 1`. Name patterns can contribute a prefix for efficient listing. Listing asks for `limit+1` to compute `hasMore`. Pattern filtering increments `missedCount` for skipped entries, then repeats listing to fill the requested count after misses.

## Persistence Behavior
This file delegates to `doListDirectoryEntries`, which may delete expired metadata and chunks. The search layer itself does not write.

## Dependencies and Integration Points
Uses `filepath.Match`, store listing through `doListDirectoryEntries`, TTL cleanup behavior in `filer.go`, and `util.FullPath` path normalization.

## Risks
For pattern matching, `nameToTest[len(prefix):]` assumes the entry name is at least as long as the prefix and aligned with listing prefix. Refill loops depend on `missedCount` and `lastFileName` moving forward to avoid repeated scans. Prefix and name pattern are documented as mutually exclusive but code allows prefix derived from pattern.

## Test Signals
No direct tests in this subset. Listing behavior is indirectly exercised by lazy listing and deletion tests through the stub store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_search.go -->
