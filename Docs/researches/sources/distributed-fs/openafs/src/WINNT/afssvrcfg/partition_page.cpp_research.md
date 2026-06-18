<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp

Purpose: Implements the wizard page for choosing whether to create an initial AFS partition and selecting a drive/partition suffix.

Important APIs/functions: `PartitionPageDlgProc`, `WizardDlgProc`, `OnInitDialog`, `OnListSelection`, `OnPartitionName`, `SavePartitionInfo`, `ShowPartitionInfo`, `CheckEnableButtons`, `CantMakePartition`, and `MustMakePartition`.

Control flow: The page refreshes drive data when the wizard reactivates. It disables partition creation if a partition already exists or the host is not/will not be a file server. First-server mode forces partition creation. Selecting a non-AFS drive auto-fills a lower-case suffix while the user has not manually typed a name. Next validates the name and advances to root-volume choices.

State and persistence: Writes `g_CfgData.configPartition`, `szPartitionName`, and `chDeviceName`; no durable partition is created until the final config page runs `ConfigPartition`.

Dependencies and integration points: Uses drive-list helpers from `volume_utils`, partition utilities, validation, common wizard handling, FastList notifications, and `g_pWiz` subclass hooks.

Risks: Wizard subclass hook removal depends on receiving `WM_DESTROY_SHEET`; repeated visits may add duplicate hooks if not balanced. `GetWindowText` buffer sizes are close to the max and may truncate without clear feedback. Disabled state can hide stale selected device/name.

Test signals: Test no file-server dependency, already-created partition, first-server forced partition, drive refresh on activation, auto-name vs manual-name behavior, invalid names, empty drive/name button disabling, and forward/back persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_page.cpp -->
