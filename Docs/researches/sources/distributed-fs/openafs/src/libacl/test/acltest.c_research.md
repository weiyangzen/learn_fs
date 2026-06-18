## sources/distributed-fs/openafs/src/libacl/test/acltest.c

Purpose: `acltest.c` is an interactive command shell for manually testing ACL externalization/internalization and rights evaluation against the protection server.

Important APIs and control flow: it initializes the protection client with `pr_Initialize`, keeps up to 20 internal ACL pointers and 20 external ACL strings, and loops reading short commands. `ex` externalizes an internal ACL. `in` internalizes an external ACL. `sa` adds a positive external ACL entry with rights converted by `Convert`. `la` lists external ACL entries using `PRights`. `cr` translates a name to ID, obtains CPS groups with `pr_GetCPS`, and calls `acl_CheckRights`. `q` exits.

State and persistence: stores ACLs in process memory only. It uses a hard-coded `/usr/afs/etc` protection configuration path and talks to a live protection server.

Dependencies and integration points: depends on `acl.h`, `prs_fs.h`, ptclient/protection server APIs, rx/xdr cleanup, and symbolic rights mapping (`read`, `write`, `mail`, `all`, `none`, or individual `rlidwka` letters).

Risks: purely interactive and not scripted. Several code paths use unchecked `scanf` and fixed buffers. The `la` negative-rights branch appears to call `scanf(ptr, ...)` where `sscanf` was likely intended. `sa` performs manual string surgery that may be fragile for multi-digit ACL counts.

Test signals: useful for manual smoke testing, especially `sa`, `in`, `ex`, `la`, and `cr` command sequences against known protection users/groups.
