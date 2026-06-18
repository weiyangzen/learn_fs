# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/task.h

Purpose: declares the task protocol shared by UI dialogs and the background task executor. It defines parameter blocks for opening cells, changing/creating/deleting users and groups, setting membership and ownership lists, translating names to ASIDs, listening for object notifications, and changing cell max IDs.

Important APIs/types: the `TASK` enum is the central dispatch contract consumed by `PerformTask` in `task.cpp` and by callers through `StartTask`. `TASKPACKETDATA` is the common return structure carrying cell/object IDs, ASID/action lists, search pattern, object type/properties, membership flag, and random key bytes. `TASKDATA(_ptp)` casts `ptp->pReturn` to this return payload.

State and dependencies: the header depends on AFS admin-server types such as `ASID`, `ASIDLIST`, `ASOBJPROP`, `AFSADMSVR_CHANGEUSER_PARAMS`, and `ACCOUNTACCESS` through the umbrella application headers. It does not persist state, but it encodes ownership expectations in comments: many enum cases take heap-allocated structs, cloned strings, or ASID lists that `task.cpp` frees.

Risks and test signals: adding a task requires updating the enum, caller payload type, dispatcher, result cleanup, and possibly `FreeTaskPacket`. Tests should verify every task id has a dispatch branch and that payload/list ownership matches the comments.
