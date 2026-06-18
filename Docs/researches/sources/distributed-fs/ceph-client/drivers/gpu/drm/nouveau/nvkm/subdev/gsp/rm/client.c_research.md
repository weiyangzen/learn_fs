<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c

## Purpose
Manages GSP-RM client ID allocation, construction, and destruction.

## Important APIs, Types, And Functions
Exports `nvkm_gsp_client_ctor` and `nvkm_gsp_client_dtor`.

## Control Flow
Constructor requires `gsp->rm`, allocates an ID from `gsp->client_id.idr`, initializes client backpointers and event list, and calls the selected RM API client constructor with handle `NVKM_RM_CLIENT(id)`. Destructor frees the RM client object if allocated, removes the ID under mutex, and clears `client->gsp`.

## State And Persistence
Persists IDR entries, client object handle, event list, and GSP backpointer until destruction.

## Dependencies And Integration Points
Depends on RM API `client->ctor`, GSP RM allocation/free helpers, and `handles.h` handle encoding.

## Risks And Edge Cases
ID allocation failure aborts construction. Destruction must run after dependent events/objects are freed to avoid dangling event callbacks.

## Test Signals
Unique client handles, successful RM root allocation, and clean IDR removal during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c -->
