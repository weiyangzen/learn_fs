# sources/distributed-fs/lizardfs/src/master/datacachemgr.h

Purpose: declares the data cache manager API.

Important APIs/functions: `dcm_open(inode, sessionid)`, `dcm_access(inode, sessionid)`, `dcm_modify(inode, sessionid)`, `dcm_init`, and `dcm_clear`.

Control flow: callers open/check cache validity, mark access valid, invalidate other sessions after modification, and initialize/reset the manager.

State and persistence: implementation-owned volatile cache state.

Dependencies and integration: included by master filesystem/client operation paths.

Risks: C-style API does not expose capacity or synchronization constraints.

Test signals: no direct tests in this subset.
