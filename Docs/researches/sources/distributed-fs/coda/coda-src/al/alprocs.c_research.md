# sources/distributed-fs/coda/coda-src/al/alprocs.c

Purpose: Implements the access-list (AL) library surface used by Coda servers and tools to allocate access lists and CPS sets, convert between internal and external text forms, translate names through the protection database, and compute effective rights.

Important APIs/functions: `AL_NewAlist`, `AL_FreeAlist`, `AL_htonAlist`, `AL_ntohAlist`, `AL_NewExternalAlist`, `AL_Internalize`, `AL_Externalize`, `AL_NewCPS`, `AL_GetInternalCPS`, `AL_GetExternalCPS`, `AL_CheckRights`, `AL_NameToId`, `AL_IdToName`, `AL_IsAMember`, `CmpPlus`, `CmpMinus`, and debug print helpers. The global `AL_MaxExtEntries` bounds external ACL conversion.

Control flow: Allocation routines size flexible-array structs and abort on allocation failure. Byte-order conversion routines no-op when host order already matches network order, otherwise swap header fields and entry arrays in place. `AL_Externalize` emits a counted text form, translating numeric IDs to PDB names when possible. `AL_Internalize` parses counts, resolves names back to IDs, fills an `AL_AccessList`, then sorts plus entries ascending and minus entries with `CmpMinus`. `AL_CheckRights` walks sorted ACL plus/minus entries against the CPS inclusion list, ORs matching positive rights, ORs matching negative rights, and returns `plus & ~minus`.

State and persistence: This file owns only heap-allocated AL/CPS buffers. Persistent identity and membership state is read through `PDB_db_open`, `PDB_readProfile`, `PDB_lookupByName`, and `PDB_lookupById`; `AL_Initialize` asserts that the PDB exists but does not mutate it.

Dependencies and integration: Depends on `prs.h`, `pdb.h`, `al.h`, RPC2/Coda utility logging, byte-order APIs, and the PDB profile array implementation. VICE and tools call this layer for authorization checks and CPS materialization.

Risks and test signals: The external ACL/CPS buffer sizing is an estimate and uses `sprintf`/`strcpy`; malformed or unexpectedly long data could overflow if invariants fail. `AL_Internalize` sorts minus entries using an offset based on `m` rather than `p`, which is suspicious because minus entries start after plus entries. Most failures return errno-style values, but allocation failures abort. `AL_CheckRights` assumes sorted CPS and ACL sections. `altest.c` is the interactive coverage signal for these APIs.
