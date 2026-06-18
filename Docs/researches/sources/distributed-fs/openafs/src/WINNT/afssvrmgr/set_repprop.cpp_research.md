# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.cpp

Purpose: Implements the fileset replication properties sheet, focused on listing, adding, deleting, and releasing replica sites for a read-write fileset.

Important APIs/functions: `Filesets_ShowReplication` starts `taskSET_REPPROP_INIT`; `Filesets_OnEndTask_ShowReplication` opens/focuses the replication properties sheet; `Filesets_RepSites_DlgProc` manages the replica-site list tab; `Filesets_RepSites_OnInitDialog` sets identity fields and populates via `UpdateDisplay_Replicas`; `Filesets_RepSites_OnDelete` calls `Filesets_Delete` for selected replica.

Control flow: The init task resolves a RW fileset and status. Existing sheets are found with `PropCache_Search(pcSET_REP, lpiRW)`. The list registers `FastList` text callbacks and column notifications, stores/restores `gr.viewRep`, subscribes to `WHEN_SETS_CHANGE`, and refreshes the list on dispatch notifications. Commands route to create replica, delete selected site, and release RW fileset.

State and persistence: Dialog state consists of `SET_REPPROP_PARAMS` with requested/RW identities and a copied `FILESETSTATUS`. Column layout persists through `gr.viewRep` and `FL_StoreView`/`FL_RestoreView`. Actual replication changes are performed by delegated tasks invoked through other modules.

Dependencies/integration: Uses `set_createrep.h`, `set_delete.h`, `set_release.h`, `display.h`, `columns.h`, `propcache.h`, and the command/display infrastructure. It subclasses the replica FastList to support column menu commands.

Risks: The `lpiTarget` parameter to `Filesets_ShowReplication` is accepted but not used in this file. Subclass procedure pointer is static and shared across instances. The list refresh depends on notification ordering and valid `prp` lifetime.

Test signals: Open from RW/replica identity, failed init, duplicate property sheet focus, add/delete/release commands, column resize persistence, `WHEN_SETS_CHANGE` refresh, and context menu header behavior.
