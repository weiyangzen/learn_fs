<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp

Purpose: Implements the config-manager Partitions tab for listing configured/exported AFS partitions, adding registry partition entries, removing unexported entries, and launching salvage.

Important APIs/functions: `PartitionsPageDlgProc`, `UpdatePartitionList`, `OnCreatePartitions`, `OnRemove`, `OnSalvage`, `ShowPartitions`, `GetPartitionTableFromRegistry`, `GetPartitionTableFromVos`, `DiskSpaceToString`, and `CheckEnableSalvage`.

Control flow: Init sets up FastList columns/images, reads registry partition entries through cfg, optionally reads exported partition/space data through vos when file server is configured, then merges both views into the list. Create opens `CreatePartition` and refreshes on success. Remove refuses exported partitions, confirms deletion, calls `cfg_HostPartitionTableRemoveEntry`, and removes the item from UI. Salvage validates file-server state, runs the salvage dialog, shows results, then refreshes the list.

State and persistence: Uses static selected item, list handles, localized Yes/No strings, and remembered file-server config state. Durable changes include cfg partition-table removal/addition and salvage side effects on server data. VOS partition data is read-only.

Dependencies and integration points: Integrates FastList/image-list helpers, app-library icons, `partition_utils`, `create_partition_dlg`, `salvage_results_dlg`, OpenAFS vos/client/cfg APIs, and global handles `g_hServer`/`g_hCell`.

Risks: The merged display assumes registry entries are authoritative and vos entries are a subset. Removal updates UI but not necessarily the cached partition table. VOS enumeration uses a fixed `MAX_PARTITIONS` of 26. `DiskSpaceToString` returns a static buffer reused for both total/free columns; correctness depends on FastList copying text immediately.

Test signals: Test no partitions, registry-only partition, exported partition with size/free data, VOS failures, remove exported refusal, remove unexported success/failure, create refresh, salvage disabled when no partitions, and configFS changes while page is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partitions_page.cpp -->
