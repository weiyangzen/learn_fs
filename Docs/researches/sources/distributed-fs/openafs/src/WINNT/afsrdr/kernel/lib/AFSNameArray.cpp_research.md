# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNameArray.cpp

## Purpose

`AFSNameArray.cpp` manages `AFSNameArrayHdr` path arrays used by the Windows redirector to represent a sequence of `AFSDirectoryCB` entries from a root through path components. It allocates, populates, clones, extends, backs up, resets, dumps, and frees these arrays while maintaining directory `NameArrayReferenceCount` references.

## Important APIs, types, and functions

`AFSInitNameArray` allocates and optionally seeds an array. `AFSPopulateNameArray` initializes an array with a volume root. `AFSPopulateNameArrayFromRelatedArray` copies entries from a related array up to a target directory or the related array end. `AFSFreeNameArray` decrements held directory references and frees the allocation. `AFSInsertNextElement` appends a directory and rejects recursive FID reuse. `AFSBackupEntry` removes the current element and may also remove a mount-point entry when backing out of a volume root. `AFSGetParentEntry`, `AFSResetNameArray`, and `AFSDumpNameArray` provide parent lookup, reuse, and diagnostics.

## Control flow

Initialization chooses capacity from the caller or `Specific.RDR.NameArrayLength`, allocates a header plus element array, zeroes it, sets `MaxElementCount`, and optionally fills element zero with directory name, file id, root flag, cursor, count, and reference increment. `AFSPopulateNameArray` seeds from the volume root associated with the target directory; the `Path` parameter is used only for tracing. Related-array population copies live directory/file-id data from another array and increments each copied directory reference.

Insertion checks capacity, scans existing entries with `AFSIsEqualFID` to prevent recursion, advances `CurrentEntry`, increments array and directory counts, and fills component, file id, and root flag. Backup decrements the current directory reference, clears the entry, decrements count, moves the cursor back, returns the new current directory, and recursively removes a paired mount point when a volume-root entry is removed. Reset decrements current references, zeroes the array footprint, restores capacity, and optionally seeds a new first entry.

## State and persistence behavior

The arrays are transient in-memory traversal state. Their durable effect is reference accounting: populate/insert/copy increment directory counts, while free/reset/backup decrement them. `Count`, `MaxElementCount`, `CurrentEntry`, `LinkCount`, and root flags encode active path traversal state.

## Dependencies and integration points

The module depends on `AFSRDRDeviceObject` configuration, OpenAFS pool wrappers, debug tracing, `AFSDirectoryCB` object/volume metadata, interlocked counters, `AFSIsEqualFID`, and root semantics based on vnode `1`. It integrates with path parsing, mount-point traversal, related-open handling, and directory lookup logic elsewhere in the redirector.

## Risks and test signals

`AFSPopulateNameArray` does not parse `Path`; callers must append components separately. Many functions assume valid non-null directory/object/volume pointers. `AFSResetNameArray` zeroes based on the current global configured length instead of the array's original `MaxElementCount`, which can mismatch explicit allocations. `AFSDumpNameArray` walks until a null `DirectoryCB` rather than `Count`. Related-array population does not visibly check destination capacity. Tests should cover default and explicit capacities, root flagging, reference-count balance, related-array copying, insertion recursion rejection, backup from normal and volume-root entries, parent lookup edge cases, reset reuse, and dump safety on corrupted arrays.
