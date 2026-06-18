# sources/distributed-fs/openafs/src/util/secutil_nt.h

Purpose: Public header for Windows security helper APIs.

Important APIs and types: Defines `WELLKNOWN_TRUSTEE_ID` with `WorldGroup` and `LocalAdministratorsGroup`. Declares `ObjectDaclEntryAdd(HANDLE, SE_OBJECT_TYPE, WELLKNOWN_TRUSTEE_ID, DWORD, ACCESS_MODE, DWORD)`.

Control flow and state: Header-only declarations; all state is per-call in `secutil_nt.c`.

Dependencies and integration: Includes `windows.h` and `aclapi.h`, so it is Windows-specific. Consumers use it when they need to add standard ACL entries without duplicating SID construction.

Risks and test signals: The enum is intentionally small; adding trustees requires implementation support. Including this header in non-Windows code would fail. Tests should verify that resulting DACLs grant expected access.
