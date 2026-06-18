# sources/distributed-fs/coda/coda-src/vol/volres.h

Purpose: declares resolution-log helper functions used by the volume/vnode layer.

Important APIs: `InitVolLog(int)`, `AllocateResLog(int, VnodeId, Unique_t)`, and `DeAllocateVMResLogListHeader(int, VnodeId, Unique_t)`.

Control flow/state: implementations are elsewhere, but declarations indicate volume resolution state can be initialized, allocated per vnode, and deallocated for VM log headers.

Dependencies/integration: included by `recovb.cc`, where vnode replacement may interact with resolution log allocation. Risks are minimal in this header but include weak type specificity (`int` volume/index arguments) and no transaction annotations. Test signals: build resolution-enabled paths, vnode writeback with `AllowResolution && V_RVMResOn`, and deallocation on vnode deletion.
