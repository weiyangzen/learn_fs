<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h

Purpose: Declares the modal partition-creation entry point.

Important APIs/functions: `CreatePartition(HWND hParent)` returns true when the dialog successfully added at least one partition.

Control flow: No implementation logic; consumers call it from the partitions property page and refresh their lists on true.

State and persistence: None in the header. Implementation writes host partition table entries.

Dependencies and integration points: Requires Win32 `HWND`; included by `partitions_page.cpp`.

Risks: The boolean return only indicates at least one successful add, not which partition was added or whether the cached partition table was refreshed.

Test signals: Verify callers refresh partition displays after true and handle false without assuming failure vs cancel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/create_partition_dlg.h -->
