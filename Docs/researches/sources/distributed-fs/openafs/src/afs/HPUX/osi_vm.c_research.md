# sources/distributed-fs/openafs/src/afs/HPUX/osi_vm.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_vm.c

Purpose: provides HP-UX VM/cache invalidation hooks for the generic AFS vcache layer.

Important APIs/types/functions: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush-vcache returns `EBUSY` if reference count or opens indicate active use. Store/flush/truncate page hooks are mostly no-ops. `osi_VM_TryToSmush` purges delayed write buffers and invalidates free buffers unless the vnode is marked text.

State/persistence: affects HP-UX buffer cache state for AFS vnodes through `mpurge` and `binvalfree`; does not directly persist data.

Dependencies/integration: called by shared AFS cache invalidation, callback revocation, truncation, and vcache recycling paths. Depends on HP-UX vnode flags and buffer cache APIs.

Risks/test signals: no-op flush/truncate hooks may leave stale mapped pages on workloads that rely on VM invalidation. Test callback revocation, `fs flush`, truncation, mapped-file reads after server-side changes, and vcache recycling under references.
