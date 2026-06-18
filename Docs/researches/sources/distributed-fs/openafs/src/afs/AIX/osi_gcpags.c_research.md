# sources/distributed-fs/openafs/src/afs/AIX/osi_gcpags.c

Purpose: AIX process-table traversal and credential extraction for garbage-collecting PAGs when `AFS_GCPAGS` is enabled.

Important APIs and functions: `afs_osi_TraverseProcTable` walks active process table entries and calls `afs_GCPAGs_perproc_func`. `afs_osi_proc2cred` maps another process's user area into the current address space and returns a static copy of its credential.

Control flow: traversal checks `afs_gcpags_procsize`, locks `proc_tbl_lock` on pre-AIX 5.1, skips unused/exiting states, validates PID index and nice range, then visits each process. Credential extraction locks process-private state, attaches the user area with `vm_att`/`xmattach`, copies `U_cred`, detaches, and returns the static credential.

State and persistence: updates global `afs_gcpags` error state on sanity failures. `afs_osi_proc2cred` uses a static `afs_ucred_t` overwritten on each successful call.

Dependencies and integration: depends on AIX `struct proc` layout, process locks, address-space APIs, and the OpenAFS PAG GC callback.

Risks and test signals: binary compatibility is fragile because process struct size/layout can differ from compile-time headers. The static credential return is not reentrant. Signals include successful PAG cleanup without PID/nice sanity errors.
