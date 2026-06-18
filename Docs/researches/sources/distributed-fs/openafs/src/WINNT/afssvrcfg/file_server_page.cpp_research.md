<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp

Purpose: Implements the wizard page for choosing whether this host should be a file server.

Important APIs/functions: `FileServerPageDlgProc`, `OnInitDialog`, and `ConfigMsg`.

Control flow: First-server mode forces file-server configuration. Already-configured file servers show a message instead of options. Otherwise radio buttons set `g_CfgData.configFS` and navigation moves between admin info and database pages.

State and persistence: Mutates `g_CfgData.configFS` only. Final configuration later starts or stops file-server-related bos processes based on this state.

Dependencies and integration points: Uses common wizard handler, resource strings, and global wizard/config state. Partition and root-volume pages depend on file-server state to enable their options.

Risks: Stale downstream choices may remain selected when file-server selection changes; later pages mask some of this through disabled flags. No validation beyond first-server forcing.

Test signals: Test first-server forced mode, already-configured message, radio toggles, downstream partition enablement, and forward/back navigation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/file_server_page.cpp -->
