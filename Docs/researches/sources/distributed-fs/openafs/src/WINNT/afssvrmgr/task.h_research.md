# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/task.h

Purpose: declares the AFS Server Manager async task protocol.

Important API/types: packet structs wrap UI-control population and cell-opening requests: `MENUTASK`, server/aggregate/fileset enum packets, `SET_LOOKUP_PACKET`, `OPENCELL_PACKET`, and `SUBSET_TO_LIST_PACKET`. The `TASK` enum lists every task id and expected `lpUser` type. `TASKPACKETDATA` is the shared return payload containing identities, text, status structs, preferences, admin/host/key lists, ghost flags, and other task results. `TASKDATA(ptp)` casts `pReturn`.

Control flow contract: `CreateTaskPacket`, `PerformTask`, and `FreeTaskPacket` are installed in the AfsAppLib task queue. Callers must pass the exact packet type documented in the enum comments and inspect `TASKDATA` only after completion.

State and persistence: no direct persistence, but many packet types trigger persistent changes in `task.cpp`.

Dependencies/integration: depends on all common manager types pulled through `svrmgr.h`, plus many forward-visible packet types from included feature headers.

Risks/test signals: enum comments are the main type-safety guard; C++ cannot enforce the `lpUser` variant. Adding fields to `TASKPACKETDATA` requires updating `FreeTaskPacket` for owned allocations. Tests should verify each new task has a switch case and correct cleanup.
