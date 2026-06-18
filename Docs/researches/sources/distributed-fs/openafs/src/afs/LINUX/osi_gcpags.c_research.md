# sources/distributed-fs/openafs/src/afs/LINUX/osi_gcpags.c

## Purpose
This file supports PAG garbage collection on Linux by traversing process credentials and extracting credentials for a task when group-based PAGs are in use.

## Important APIs, types, and functions
- `afs_osi_TraverseProcTable()` walks live processes and calls `afs_GCPAGs_perproc_func`.
- `afs_osi_proc2cred(afs_proc_t *pr)` returns a static AFS credential snapshot for a process.

## Control flow and behavior
When `AFS_GCPAGS` is enabled and keyring/credential conditions permit safe group scanning, traversal enters `rcu_read_lock`, iterates `for_each_process` or legacy `for_each_task`, skips pid-zero and zombie/exited tasks, and invokes the portable PAG-GC callback. `afs_osi_proc2cred` validates process state, fills a static `afs_ucred_t` with uid and group info from the task, increments group-info references, and returns the static pointer.

## State and persistence
`afs_osi_proc2cred` uses a static credential object overwritten on each call. It increments group-info references for returned snapshots, although comments warn that freeing the static credential would be dangerous. No persistent state exists.

## Dependencies and integration points
The code integrates Linux task traversal/RCU with OpenAFS PAG garbage collection. It is disabled when keyring PAGs are used or when safe RCU/task credential access is not available.

## Risks
The static credential return is explicitly dangerous if consumers call `crfree` on it. Task credential access must match kernel RCU semantics exactly. The code is compile-time gated away for keyring support, so group-based and keyring-based PAG GC behavior diverges.

## Test signals
PAG GC tests should cover process traversal with live, exiting, and zombie tasks; group-PAG detection; reference leak checks for group info; and build variants with/without `LINUX_KEYRING_SUPPORT`, `STRUCT_TASK_STRUCT_HAS_CRED`, and RCU support.
