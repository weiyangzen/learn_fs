<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go

## Purpose
Adapts a filer store to serve a mounted subtree by translating paths between global filer paths and backend-local paths.

## Important APIs and Types
`FilerStorePathTranslator` wraps an actual store plus `storeRoot`. `NewFilerStorePathTranslator` normalizes roots. `translatePath`, `changeEntryPath`, and `recoverEntryPath` handle path conversion. The type implements all `FilerStore` methods.

## Control Flow and State
For non-root store roots, global paths have the store root prefix stripped before backend calls. Entry-mutating methods temporarily rewrite `entry.FullPath`, defer recovery, and call the backend. Find/list methods translate returned entry paths back to global paths.

## Persistence Behavior
The underlying store persists local translated paths, not the global filer prefix. KV and transaction calls pass through unchanged.

## Dependencies and Integration Points
Used by `FilerStoreWrapper.AddPathSpecificStore` to route subtrees to separate backend stores. Depends on consistent prefix matching from the wrapper.

## Risks
Path slicing assumes inputs are under `storeRoot`; misuse can panic or corrupt paths. Mutating entries in place can surprise callers if recovery is skipped by panic. KV namespace is shared with the actual store and not root-prefixed.

## Test Signals
No direct tests in this subset. Wrapper tests cover some wrapper behavior but not path translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_translate_path.go -->
