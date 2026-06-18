# sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_export.c

## Purpose
Implements pNFS metadata-server export/module operations, especially device-info encoding from LizardFS chunk and chunkserver metadata.

## Important APIs, Types, And Functions
Key helpers include chunkserver comparison/filtering/shuffling, `lzfs_int_get_randomized_chunkserver_list`, `lzfs_int_fill_chunk_ds_list`, and `lzfs_int_fill_unused_ds_list`. Export/module hooks include `lzfs_fsal_getdeviceinfo`, `lzfs_fsal_getdevicelist`, layout type/blocksize/segment/body-size accessors, `lzfs_fsal_export_ops_pnfs`, and `lzfs_fsal_ops_pnfs`.

## Control Flow
`getdeviceinfo` validates NFSv4.1 file layout, resolves the export by device id, fetches up to 4096 file chunks, fetches chunkservers, removes disconnected and duplicate-IP entries, randomizes server order, encodes stripe indices, then encodes multipath DS lists. For existing chunks it prefers chunkservers holding standard parts, then non-standard parts, then fills remaining DS slots from the randomized list. Remaining stripe entries are filled only from randomized chunkservers.

## State And Persistence Behavior
No persistent local state beyond temporary arrays. It reads chunk/chunkserver topology from the LizardFS client instance and serializes it into NFS-Ganesha XDR responses.

## Dependencies And Integration Points
Depends on FSAL/pNFS XDR helpers, `context_wrap`, `lzfs_internal`, LizardFS C API, and `MFSCommunication.h` constants. Complements `mds_handle.c` layoutget, which embeds device ids and DS wire handles.

## Risks And Edge Cases
The local `remove_if` copies from destination index `j` into source index `i`, which appears reversed and may corrupt filtering. Duplicate-IP detection assumes sorted entries and pointer arithmetic. If all chunkservers are disconnected or filtering empties the list, deviceinfo fails. Randomization uses `rand()` without visible seeding. Stripe count is capped to 4096, so very large files rely on the design assumption that every DS can serve every chunk.

## Test Signals
Needs tests for deviceinfo encoding, disconnected/duplicate filtering, empty chunkserver handling, multipath ordering, and large-file stripe cap behavior.
