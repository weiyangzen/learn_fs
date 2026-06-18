<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp

Purpose: Discovers the machine's current AFS client/server configuration before showing the wizard or config manager and populates `g_CfgData` with existing role, partition, root-volume, replication, and cell state.

Important APIs/functions: `GetCurrentConfig` drives a `PROGRESSDISPLAY` around `GetCurrentConfigState`. Checks include `IsClientConfigured`, `IsConfigInfoValid`, `StartBosServer`, `DoesAPartitionExist`, `IsFSConfigured`, `IsDBConfigured`, `IsBakConfigured`, `AreWeLastDBServer`, `DoRootVolumesExist`, `AreRootVolumesReplicated`, `IsSCSConfigured`, and `IsSCCConfigured`. `CheckConfigState` maps boolean checks to `CS_ALREADY_CONFIGURED` or `CS_NULL`.

Control flow: The scanner verifies the client is installed/configured, reads host config status and cell name, pre-fills `szCellServDbHostname` when client/server cells differ, opens cfg handles, reads partitions, and if server config is valid starts bosserver if necessary so service state can be queried. Root volume existence and replication are read from VLDB entries and stored for later wizard decisions.

State and persistence: Populates many `g_CfgData` fields, including valid client/server flags, client cell/version, server cell, partition name/device, service config states, last-DB-server flag, root volume IDs, existence flags, and replication flags. It may persistently start bosserver as a side effect. Progress/cancel state is static process-local.

Dependencies and integration points: Uses OpenAFS cfg, vos, VLDB constants, partition utilities, `PROGRESSDISPLAY`, app-library animation, logging, and global cfg handles. Root-volume helper functions are exported for the final config page to refresh unknown status.

Risks: Service discovery can mutate the system by starting bosserver. `NextStep` uses a static `nCurStep` that is not reset in `GetCurrentConfig`, so repeated runs may over-advance progress. `AreRootVolumesReplicated` assumes VLDB entries were populated by prior `DoRootVolumesExist`; missing volumes can leave default entries. Allocated strings from cfg enumeration/query are not consistently deallocated. Cancellation relies on shared booleans without synchronization.

Test signals: Test installed/uninstalled client, invalid client, invalid server, valid server with stopped bosserver, no partitions, multiple partitions, fs/db/bak/scs/scc configured combinations, last DB server detection, missing root volumes, one root volume missing, replicated/unreplicated sites, client/server cell mismatch, and cancel during scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_cur_config.cpp -->
