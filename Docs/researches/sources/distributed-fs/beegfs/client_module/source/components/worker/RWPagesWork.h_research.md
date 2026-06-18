# sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.h

## Purpose
Declares the asynchronous page read/write work item and workqueue lifecycle.

## Important APIs and types
`RWPagesWork` stores `work_struct`, app, page vector, remoting IO info, file handle type, RW type, and inode. Inline constructor allocates and initializes a work item, marks pages failed if initialization cannot reference the file, and returns null. `RWPagesWork_uninit` destroys the page vector and releases the inode file handle. Public functions create queued work, initialize/destroy/flush the global workqueue, and process work callbacks.

## State, dependencies, integration
The work item bridges the VM/page layer and BeeGFS remoting. It owns page-vector cleanup and file-handle release.

## Risks and test signals
Destructing a partially initialized work item after `RWPagesWork_init` failure can call uninit paths that assume fields are valid; current flow calls `RWPagesWork_destruct` after failed init. Tests should exercise reference failure with instrumentation and verify no double page failure/free.
