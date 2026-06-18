# sources/distributed-fs/openafs/src/util/secutil_nt.c

Purpose: Provides Windows security utilities, currently focused on adding an ACE to an object's DACL for well-known trustees.

Important APIs and helpers: Public `ObjectDaclEntryAdd()` adds access for `WorldGroup` or `LocalAdministratorsGroup`. Private `WorldGroupSidAllocate()`, `LocalAdminsGroupSidAllocate()`, and `BuildExplicitAccessWithSid()` build SID and `EXPLICIT_ACCESS` structures.

Control flow: The public function allocates a SID for the requested trustee, builds an access entry, retrieves the current DACL with `GetSecurityInfo()`, merges using `SetEntriesInAcl()`, and writes the new DACL back. It has a special path for `SE_KERNEL_OBJECT` because historical Windows service packs mishandled named pipes with `SetSecurityInfo()`, so it updates the security descriptor and calls `SetKernelObjectSecurity()`.

Dependencies and integration: Includes Windows `aclapi.h`, `windows.h`, and `secutil_nt.h`. Used by Windows server/client code that needs predictable ACL changes on objects such as files, services, or kernel objects.

Risks and test signals: Caller must pass a handle with `READ_CONTROL`/`WRITE_DAC` rights. Only two trustee ids are supported; other values return `ERROR_INVALID_PARAMETER`. Memory ownership uses `LocalFree()` for ACL/security descriptors and `FreeSid()` for SIDs. Tests are Windows ACL behavior and access checks after object creation.
