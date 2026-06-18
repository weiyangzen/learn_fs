<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp

Purpose: Implements the wizard page for choosing whether to create `root.afs` and `root.cell` root volumes.

Important APIs/functions: `RootAfsPageDlgProc`, `OnInitDialog`, and `ShowStatusMsg`.

Control flow: First-server mode forces root volume creation. Already-created root volumes show a status message. Unknown existence defaults to creating if necessary. If no partition exists/will exist, the step is disabled. If `root.afs` exists but `root.cell` does not, creation is disabled due to a known unsupported case. Otherwise radio buttons set `g_CfgData.configRootVolumes`.

State and persistence: Mutates `g_CfgData.configRootVolumes` and its disabled bit only. Durable volume creation, ACL, mount-point, and client-start operations occur later in the final configuration page.

Dependencies and integration points: Depends on root-volume and partition state from current-config discovery and partition page, common wizard helpers, and resource strings.

Risks: The partial `root.afs` exists/`root.cell` missing case is handled by silently disabling creation with a TODO rather than a specific explanatory string. Unknown existence can lead to final config doing extra checks and no-ops.

Test signals: Test first-server forced creation, already-configured roots, unknown existence, missing partition, partial root-volume state, radio choices, and downstream replication enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/root_afs_page.cpp -->
