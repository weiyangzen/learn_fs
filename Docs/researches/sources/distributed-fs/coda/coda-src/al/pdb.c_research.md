# sources/distributed-fs/coda/coda-src/al/pdb.c

Purpose: High-level protection database mutation and lookup layer. It creates, deletes, renames, clones, and changes IDs for users and groups while keeping membership lists, ownership lists, and CPS arrays consistent.

Important APIs/functions: `PDB_addToGroup`, `PDB_removeFromGroup`, `PDB_changeName`, `PDB_createUser`, `PDB_cloneUser`, `PDB_deleteUser`, `PDB_createGroup`, `PDB_deleteGroup`, `PDB_lookupByName`, `PDB_lookupById`, `PDB_bugfixes`, and `PDB_changeId`.

Control flow: Mutators open the database read/write, read affected profiles, update sorted `pdb_array` fields, write profiles, and close the shared handle. User creation allocates the next positive ID; group creation allocates the next negative ID and adds the owner as a member. Membership changes update both the group's `groups_or_members` and the member's `member_of`, then recompute CPS. Delete and ID-change flows walk all related groups/members to repair back references. `PDB_bugfixes` scans all records twice to repair historical owner/member/CPS inconsistencies.

State and persistence: Persists all changes via `PDB_writeProfile`, `PDB_deleteProfile`, and max-ID updates in `prot_users.cdb`. The logical profile state consists of positive user IDs, negative group IDs, `member_of`, `cps`, and `groups_or_members`.

Dependencies and integration: Depends on `pdb.h`, `prs.h`, `pdbarray`, profile pack/read/write helpers, and `rwcdb` through `pdbdb.c`. AL and auth code consume this database for identity and authorization.

Risks and test signals: Heavy use of `CODA_ASSERT` makes many data errors process-fatal. `PDB_deleteGroup` contains a suspicious `CODA_ASSERT(p.id == 0)` when reading groups that should exist. Recursing CPS updates can be expensive and depends on loop prevention. Name uniqueness is checked before create, but there is no visible transaction boundary across multi-record updates. `pdbtool` and `pdbarray_test` provide the main local exercisers.
