<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp

Purpose: Implements the wizard replication page for choosing whether to replicate `root.afs` and `root.cell`.

Important APIs/functions: `ReplicationPageDlgProc`, `OnInitDialog`, and `ShowStatusMsg`.

Control flow: First-server mode forces replication. Already-replicated root volumes show a message. If replication status is unknown, the page asks whether to replicate if necessary and defaults to configure. If root volumes are not/will not be configured, replication is disabled. Otherwise radio buttons set `g_CfgData.configRep`.

State and persistence: Mutates `g_CfgData.configRep` and disabled state only. Actual read-only site creation and volume releases happen in the final config page.

Dependencies and integration points: Uses root-volume state discovered by `get_cur_config.cpp`, `ConfiguredOrConfiguring`, `EnableStep`, common wizard handling, and resource strings.

Risks: Filename is misspelled `replicatition_page.cpp`, which can confuse search/build maintenance. Unknown replication status can schedule a later check and possible no-op, so UI choice is conditional. Disabled state may retain stale configure selection under the flag.

Test signals: Test first-server forced replication, already replicated, unknown status, no root volumes, radio toggles, and final config behavior when only one root volume lacks replication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/replicatition_page.cpp -->
