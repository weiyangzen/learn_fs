## sources/distributed-fs/openafs/src/libacl/acl.h

Purpose: `acl.h` defines the internal and external ACL contracts used by AFS file-server/VICE code and declares ACL allocation, conversion, rights-checking, initialization, and byte-order APIs.

Important types and APIs: `acl_accessEntry` stores a protection ID and rights mask. `acl_accessList` stores size, version, total, positive count, negative count, and an entries array; negative entries are stored backwards from the end. `ACL_MAXENTRIES` is 20. External ACLs are strings beginning with positive and negative counts, followed by name/right lines. Declared APIs include `acl_NewACL`, `acl_FreeACL`, `acl_NewExternalACL`, `acl_FreeExternalACL`, `acl_Externalize`, `acl_Internalize`, `_pr` variants with custom translation functions, `acl_Initialize`, `acl_CheckRights`, `acl_IsAMember`, `acl_HtonACL`, and `acl_NtohACL`.

State and persistence: the structure layout is used for secondary storage in VICE, so it is a persistence contract as well as a memory contract.

Dependencies and integration points: includes `afs/ptint.h` for protection server ID/name list types. `acl_CheckRights` is only declared when rxgen ptint types are available.

Risks: fixed `ACL_MAXENTRIES` and compact on-disk format mean callers must validate counts and sizes. Negative-entry reverse storage is non-obvious and must be preserved by serializers.

Test signals: exercised by `aclprocs.c`, `netprocs.c`, and interactive `test/acltest.c`.
