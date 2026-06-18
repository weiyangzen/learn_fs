# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.cpp

Purpose: Implements the confirmation dialog for releasing a read-write fileset to its replication sites.

Important APIs/functions: `Filesets_Release` opens/focuses a cached modeless release dialog. `Filesets_Release_DlgProc` handles lifecycle and OK/cancel. `Filesets_Release_OnInitDialog` formats the target server/aggregate/fileset description and defaults to normal release. `Filesets_Release_OnOK` sends `SET_RELEASE_PARAMS` to `taskSET_RELEASE`.

Control flow: Uses `PropCache` keyed by `pcSET_RELEASE` and target `LPIDENT` to prevent duplicate release dialogs for the same fileset. OK reads force-vs-normal radio state, starts the release task, and destroys the dialog; cancellation just destroys it.

State and persistence: Dialog-local only. The task packet stores `lpiRW` and `fForce`; release persistence is remote AFS volume state handled by `taskSET_RELEASE`.

Dependencies/integration: Depends on `svrmgr.h`, `set_release.h`, and `propcache.h`. Usually invoked from replication or fileset context menus.

Risks: The dialog assumes caller passes a suitable read-write fileset identity. It does not validate fileset type locally. Errors are not handled in this file after dispatch.

Test signals: Open duplicate release dialogs, normal vs force release, cancel path, and invocation on non-RW identities through higher-level command gating.
