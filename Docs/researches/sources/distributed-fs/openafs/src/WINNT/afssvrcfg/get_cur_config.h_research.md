<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h

Purpose: Declares current-configuration discovery entry points and root-volume helper checks.

Important APIs/functions: `GetCurrentConfig(HWND, BOOL&)`, `DoRootVolumesExist(BOOL&)`, and `AreRootVolumesReplicated(BOOL&)`.

Control flow: No header logic. The final configuration page uses the root-volume helpers when startup could not determine status.

State and persistence: Functions declared here mutate `g_CfgData` in implementation and may query/start server components.

Dependencies and integration points: Requires `afs_status_t`, Win32 types, and the global configuration environment from `afscfg.h`.

Risks: Function names imply pure queries, but implementation has side effects and depends on initialized global handles.

Test signals: Verify callers only invoke root-volume checks after `g_hCell`/vos context is available and handle nonzero AFS statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.h -->
