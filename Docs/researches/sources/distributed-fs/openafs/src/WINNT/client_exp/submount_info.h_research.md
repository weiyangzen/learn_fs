## sources/distributed-fs/openafs/src/WINNT/client_exp/submount_info.h

Purpose: Defines the data model for AFS submount registry edits.

Important APIs/types: `SUBMT_INFO_STATUS` distinguishes null, added, changed, and deleted entries. `CSubmountInfo` stores share name, path name, and status. `SUBMT_INFO_ARRAY` is an MFC pointer array of `CSubmountInfo*`.

Control flow/state: Inline getters and setters mutate value fields; no persistence occurs in this class.

Dependencies/integration: Includes `afxtempl.h`; used by submount dialog and add/edit dialog code.

Risks/tests: Pointer-array ownership is external and can leak/double-free if callers disagree. Test add/change/delete lifecycles and copy-constructor behavior.
