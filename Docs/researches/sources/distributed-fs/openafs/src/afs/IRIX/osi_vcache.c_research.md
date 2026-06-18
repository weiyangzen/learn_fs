# sources/distributed-fs/openafs/src/afs/IRIX/osi_vcache.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_vcache.c

Purpose: implements IRIX vcache/vnode allocation and initialization, including IRIX behavior descriptors and page-cache structures.

Important APIs/types/functions: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: new vcaches are allocated, zeroed, assigned a unique vnode number, initialized with a named rw semaphore, and later populated with behavior descriptors, behavior head, mapping pointers, trace state, bitlocks, file lock mutex, buffer lock, page cache, VFS/type, page counters, vnode lists, and default fields. Eviction only flushes vcaches without refs, opens, or unlinked-delete state.

State/persistence: all state is in-memory vnode/vcache infrastructure. `afsvnumbers` monotonically supplies vnode numbers; semaphores and mutexes live with the vcache.

Dependencies/integration: depends on `makesname`, `Afs_vnodeops`, `afs_globalVFS`, IRIX behavior and vnode page-cache APIs, and OpenAFS vcache state.

Risks/test signals: high-risk initialization order: missing behavior setup, lock init, or pcache reinit can crash later VOP/VM paths. Test vcache allocation/reuse, vnode hold/release, page-cache reclaim, vnode tracing builds, and eviction with mapped/dirty pages.
