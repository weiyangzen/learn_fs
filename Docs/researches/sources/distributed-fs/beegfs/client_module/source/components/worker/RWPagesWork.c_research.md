# sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.c

## Purpose
Implements asynchronous read/write page work items for BeeGFS chunk page vectors using a kernel workqueue.

## Important APIs and control flow
`RWPagesWork_initworkQueue`, `destroyWorkQueue`, and `flushWorkQueue` manage the global workqueue. `RWPagesWork_init` records app/inode/page vector/RW type, references the file handle with `_RWPagesWork_initReferenceFile`, fills `RemotingIOInfo`, and initializes `kernelWork`. `RWPagesWork_createQueue` constructs a work item, queues it, and marks all pages failed if construction or queueing fails. `RWPagesWork_process` casts the `work_struct` to `RWPagesWork` because it is the first struct member, then `RWPagesWork_processQueue` calls `FhgfsOpsRemoting_rwChunkPageVec`, logs result, and destructs the work item.

## State, dependencies, integration
Global state is `rwPagesWorkQueue`. Each work item owns the page vector and a referenced file handle until destruction. It depends on `FhgfsInode`, `FhgfsOpsPages`, `FhgfsOpsRemoting`, and kernel workqueue APIs.

## Risks and test signals
The cast from `work_struct*` to `RWPagesWork*` relies on `kernelWork` being the first member. Queueing before global init would dereference a null workqueue. Tests should cover read/write failure marking, reference acquire/release, queue failure, workqueue flush/destroy, and layout assumptions.
