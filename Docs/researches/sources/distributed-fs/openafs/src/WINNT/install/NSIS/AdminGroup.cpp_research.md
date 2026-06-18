<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp

Purpose: Command-line utility for NSIS installers to create or remove the local `AFS Client Admins` group and initially populate it with members of the built-in Administrators group.

Important APIs, types, and functions: `LookupAliasFromRid` resolves a localized built-in alias name from a RID. `createAfsAdminGroup` calls `NetLocalGroupAdd`. `initializeAfsAdminGroup` resolves Administrators, enumerates members with `NetLocalGroupGetMembers`, and adds them to `AFS Client Admins` with `NetLocalGroupAddMembers`. `removeAfsAdminGroup` deletes the group. `main` parses `-create` and `-remove`.

Control flow and state: On `-create`, the utility creates the group, treats `ERROR_ALIAS_EXISTS` as success, and only populates members after a new group is created. On `-remove`, it ignores deletion status and exits success.

Persistence and dependencies: Persists local SAM group and membership changes. Depends on `netapi32`, `advapi32`, well-known SID APIs, and administrative privileges.

Integration points: NSIS installation/uninstallation uses this tool; WiX `afscustom.cpp` contains similar embedded logic.

Risks: Existing group membership is not reconciled or updated when the group already exists. Error logging has malformed `fprintf` format arguments in some paths. Removing ignores failures. The fallback English `Administrators` name can fail on localized systems if SID lookup fails.

Test signals: Run on localized and English systems, create existing/nonexisting group cases, verify copied members, remove group, and test non-admin failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp -->
