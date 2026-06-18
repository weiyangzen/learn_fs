## sources/distributed-fs/openafs/src/libacl/aclprocs.c

Purpose: `aclprocs.c` implements allocation, external/internal string conversion, protection-server name/ID translation, rights evaluation, membership tests, and a small freelist allocator for ACL objects.

Important APIs and functions: `acl_NewACL` and `acl_NewExternalACL` allocate internal and external ACL buffers, reusing `freeList` entries when possible. `acl_FreeACL` and `acl_FreeExternalACL` return buffers to the freelist. `acl_Externalize_pr` converts IDs to names via a caller-supplied function and emits external string format. `acl_Internalize_pr` parses external strings, translates names to IDs, stores positive entries at the front and negative entries at the back, and sorts them with `CmpPlus`/`CmpMinus`. `acl_CheckRights` intersects a caller's CPS group list with positive and negative ACL entries, grants all rights to `SYSADMINID`, and returns positive rights masked by negative rights. `acl_Initialize` checks the package version and initializes a pthread mutex when enabled. `acl_IsAMember` scans a CPS list.

Control flow: internalization starts with count parsing and limit checks, allocates an ACL, reads positive entries in order, reads negative entries into the reversed storage region, calls the name-to-ID translator once with all names, rejects `ANONYMOUSID`, then sorts positive ascending and negative descending. Rights checking walks sorted ACL and CPS arrays in merge style, accumulating matches.

State and persistence: process-global `freeList` caches allocations, protected by `acl_list_mutex` in pthread builds. Internal ACLs are storage-compatible with file-server ACL persistence and may later be converted to network order.

Dependencies and integration points: depends on ptserver client APIs `pr_IdToName` and `pr_NameToId`, rx/xdr types, OpenAFS `opr_Verify`, and constants like `ANONYMOUSID` and `SYSADMINID`.

Risks: allocation failures sometimes abort rather than returning errors. `acl_FreeExternalACL` assumes non-null input. External parsing uses `%63s` and expects tab-delimited rights. The freelist never releases memory back to the system. `acl_CheckRights` assumes sorted group CPS input for merge behavior.

Test signals: `test/acltest.c` exercises allocation, externalization/internalization, rights conversion, and protection-server-backed rights checks interactively.
