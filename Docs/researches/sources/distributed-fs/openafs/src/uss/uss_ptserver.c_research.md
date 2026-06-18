
# sources/distributed-fs/openafs/src/uss/uss_ptserver.c

Purpose: `uss_ptserver.c` wraps Protection Server operations for `uss`: initialize the PTS client, create a user entry with optional desired UID, delete a user entry, and translate a name to UID.

Important APIs and functions: `InitThisModule()` lazily calls `pr_Initialize()` with authenticated security, config directory, and cell. `uss_ptserver_AddUser()` calls `pr_CreateUser()`, handles existing name or ID cases, verifies name-to-ID mappings with `pr_SNameToId()`, and writes the resulting ID string to the caller buffer. `uss_ptserver_DelUser()` calls `pr_Delete()` and treats missing entries as warning/success. `uss_ptserver_XlateUser()` translates a name and rejects `ANONYMOUSID`.

Control flow: add initializes PTS, handles dry-run by only filling the requested UID string, then creates or reconciles an existing entry. Delete and translate initialize lazily and then perform one server operation.

State and persistence: module state is just `initDone`; persistent effects are Protection Database entries. It reads global `uss_DesiredUID`, `uss_DryRun`, `uss_Cell`, `uss_ConfDir`, verbosity, and program name.

Dependencies and integration: `uss.c` uses this before KAS creation during add and after KAS deletion during delete; `SaveRestoreInfo()` uses translation before volume deletion. Depends on OpenAFS PTS client libraries and error tables.

Risks: add is permissive for preexisting users if the mapping matches, which can mask partial previous runs. Dry-run with no desired UID records `0`, so downstream dry-run paths may see an unrealistic UID. Test signals should include PREXIST, PRIDEXIST with matching/mismatched mappings, missing delete, ANONYMOUSID translation, and PTS initialization failure.
