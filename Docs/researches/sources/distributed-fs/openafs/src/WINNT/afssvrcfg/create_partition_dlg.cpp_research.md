<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp

Purpose: Implements the config-manager modal dialog for adding AFS partition-table entries from an available drive list.

Important APIs/functions: `CreatePartition` opens `IDD_CREATE_PARTITION` and returns whether a partition was added. `DlgProc` handles help, create/close, drive selection, name edits, activation refresh, notifications, and resizing. `OnCreate` validates the partition name, constructs `?:` device and `/vicepX` partition strings, checks duplicates with `DoesPartitionExist`, and calls `cfg_HostPartitionTableAddEntry`.

Control flow: Init wires resize behavior and drive-list setup. Selecting a non-AFS drive auto-fills a one-letter partition suffix when the user has not typed a name. Create is enabled only when a drive and partition name exist. After successful creation, the dialog remains open with the name field cleared and `bCreated` set.

State and persistence: Uses static dialog state for selected item, auto-name flag, current buffers, and `bCreated`. Durable state is the host partition table entry written through the cfg library; the file server must later restart/export it.

Dependencies and integration points: Uses FastList drive-list helpers from `volume_utils`, `partition_utils` cached table checks, validation helpers, resource strings, and `g_hServer`/`g_LogFile`.

Risks: `GetWindowText` size arguments use character counts inconsistently with buffer byte sizes. Duplicate checking compares a constructed `/vicep` name through `A2S`, while auto-fill checks `viceX`, so naming conventions must stay aligned. The dialog does not refresh the cached partition table after adding, so repeated duplicate checks may depend on external refresh.

Test signals: Test empty/no-drive disabled state, auto-name behavior, duplicate partition names, invalid names, successful add, activation-time drive refresh, resize behavior, and cfg API failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.cpp -->
