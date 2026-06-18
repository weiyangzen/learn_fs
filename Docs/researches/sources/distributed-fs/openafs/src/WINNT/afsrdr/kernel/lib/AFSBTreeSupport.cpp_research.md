<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp

## Purpose
`AFSBTreeSupport.cpp` implements the redirector's small in-memory binary-search-tree primitives for directory entries and object hash entries. The file is not a general balanced B-tree implementation despite the name; it maintains unbalanced left/right/parent pointer trees keyed by precomputed CRC or low-file-id hash values. These helpers are used by directory enumeration, lookup, create, delete, close, and object-info indexing paths to find `AFSDirectoryCB` entries by case-sensitive name hash, case-insensitive name hash, DOS short-name hash, and `AFSBTreeEntry` hash.

## Important APIs, Types, and Functions
- `AFSLocateCaseSensitiveDirEntry`, `AFSInsertCaseSensitiveDirEntry`, and `AFSRemoveCaseSensitiveDirEntry` operate on `AFSDirectoryCB::CaseSensitiveTreeEntry`, where `HashIndex` is usually `AFSGenerateCRC(name, FALSE)`.
- `AFSLocateCaseInsensitiveDirEntry`, `AFSInsertCaseInsensitiveDirEntry`, and `AFSRemoveCaseInsensitiveDirEntry` operate on `AFSDirectoryCB::CaseInsensitiveTreeEntry`. Equal case-insensitive hashes are represented as a forward/back list through `AFSDirectoryCB::CaseInsensitiveList`, with the head flagged by `AFS_DIR_ENTRY_CASE_INSENSTIVE_LIST_HEAD`.
- `AFSLocateShortNameDirEntry`, `AFSInsertShortNameDirEntry`, and `AFSRemoveShortNameDirEntry` index optional 8.3 short names through `AFSDirectoryCB::Type.Data.ShortNameTreeEntry`.
- `AFSLocateHashEntry`, `AFSInsertHashEntry`, and `AFSRemoveHashEntry` are type-agnostic tree helpers for `AFSBTreeEntry`, used by volume/object hash trees such as `VolumeCB->ObjectInfoTree.TreeHead`.
- Core structures come from `AFSStructs.h`: `AFSBTreeEntry` carries `HashIndex`, `leftLink`, `rightLink`, and `parentLink`; `AFSDirectoryCB` embeds three tree entries plus list links, name information, object backpointer, and flags.

## Control Flow
All locate functions follow the same search pattern: return `STATUS_INVALID_PARAMETER` if the root is `NULL`, check the root key first, then walk right for greater keys and left for smaller keys until a match or branch end. Case-sensitive and short-name locators initialize the output pointer to `NULL` and otherwise return `STATUS_SUCCESS` even when no entry is found; the generic hash locator starts with `STATUS_NOT_FOUND` and only switches to `STATUS_SUCCESS` on an actual match.

Insert functions require an existing root and walk until a missing child link is found. The inserted node's parent pointer is written to the current node. Duplicate hashes are rejected for case-sensitive, short-name, and generic hash trees. The case-insensitive insert path is different: an equal hash is appended to the same-hash `CaseInsensitiveList`, while only newly inserted tree children are marked as list heads.

Remove functions splice out a node without rebalancing. If the removed node has no children, the parent child pointer or root pointer is cleared. If it has a right child, the right child replaces it at the parent/root. If it also has a left child, the left child is attached to the left-most descendant of the right subtree. If it has only a left child, that child replaces it. The removed node's tree pointers are then cleared. Case-insensitive removal has two extra branches: non-head list entries are removed only from the same-hash list, and a removed list head with a following list entry promotes that following entry into the tree position with the old head's left/right/parent links.

## State and Persistence Behavior
This file mutates only in-memory kernel control blocks. It does not allocate, free, persist, or call the cache manager or service directly. The persistent effect is indirect: these pointer trees determine whether later filesystem operations can find, remove, or verify directory entries and object-info records. Removed nodes have tree/list links nulled to prevent stale parent/child references, but lifetime ownership is handled elsewhere by directory-entry/object-info teardown functions.

The helpers assume callers hold the relevant tree lock. There is no internal synchronization. `AFSCommSupport.cpp`, `AFSCleanup.cpp`, `AFSClose.cpp`, and name-management helpers acquire directory `TreeLock` or volume object-tree locks before manipulating these trees.

## Dependencies and Integration Points
The file includes `AFSCommon.h` for prototypes, flags, debug tracing, and Windows kernel status types. Direct consumers include directory enumeration and verification in `AFSCommSupport.cpp`, name insertion/removal helpers such as `AFSRemoveNameEntry`/`AFSDeleteDirEntry`, and close-time object tree cleanup in `AFSClose.cpp`. The generic hash helpers integrate with object lookup through `AFSCreateLowIndex`, `AFSFindObjectInfo`, and `VolumeCB->ObjectInfoTree`.

The directory helpers are tightly coupled to `AFSDirectoryCB` fields populated by `AFSInitDirEntry` and metadata paths: name CRCs must already be set, `AFS_DIR_ENTRY_INSERTED_SHORT_NAME` must track short-name-tree membership, and `AFS_DIR_ENTRY_NOT_IN_PARENT_TREE` controls whether cleanup/delete code calls name removal.

## Risks and Edge Cases
- The trees are unbalanced. Directory or object insertion patterns with monotonic hash order can degrade lookup, insertion, and removal to linear behavior.
- The case-sensitive and short-name locate APIs return success for "not found" with `*DirEntry == NULL`, while `AFSLocateHashEntry` returns `STATUS_NOT_FOUND`. Callers must not treat status alone as proof of a directory hit.
- Hash collisions are mostly treated as errors. Case-sensitive name CRC collisions and short-name hash collisions can cause insert failures and dropped/rebuilt entries even if the original names differ.
- `AFSRemoveCaseInsensitiveDirEntry` temporarily returns through `try_return(ntStatus)` while `ntStatus` is still initialized to `STATUS_UNSUCCESSFUL` for non-head and promoted-head paths, but `try_exit` overwrites it to `STATUS_SUCCESS`. That relies on the local `try_return` macro routing through cleanup, not a direct return.
- The helpers do not validate that `DirEntry`/`FileIDEntry` belongs to the passed root. Removing a foreign or already-unlinked node can corrupt another tree if callers violate the ownership contract.
- All pointer fields are untyped `void *` links cast back to control-block types, so structure misuse will fail at runtime rather than compile time.

## Test Signals
Useful signals are directory enumeration and lookup behavior under mixed-case names, short-name-enabled/disabled configurations, and deletes/renames that remove tree entries. Tests should exercise root removal, leaf removal, one-child and two-child removal, case-insensitive same-hash chains, short-name collisions, and object-info hash removal on final close. Kernel debug traces for insert/remove collisions and `ASSERT` coverage around tree locks are the main in-tree observability hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSBTreeSupport.cpp -->
