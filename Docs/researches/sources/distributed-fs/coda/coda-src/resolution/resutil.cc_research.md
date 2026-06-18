<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resutil.cc

Purpose: shared resolution utilities for host lookup, inbound connection registration, inconsistency marking, store-id allocation, return-code filtering, inconsistency-list serialization, status aggregation, and directory-plus-ACL packaging.

Important APIs/control flow: `FindHE` searches parsed host log entries. `RS_NewConnection` records `conninfo`. `RS_MarkInc` marks an object inconsistent under a transaction. `AllocStoreId` uses `ThisServerId` plus `startuptime + VMCounter`. `CheckRetCodes` and `CheckResRetCodes` derive surviving host sets from RPC results. `AddILE`, `BSToDlist`, `DlistToBS`, `ParseIncBSEntry`, `AllocIncBSEntry`, `CompareIlinkEntry`, and `CleanIncList` manage inconsistency lists. `ObtainResStatus` and `GetResStatus` produce status summaries. `Dir_n_ACL` copies directory bytes, ACL, and root quotas into one buffer for transfer.

State/persistence: mutates connection-info table, vnode inconsistency bits, and the global store-id counter. Other utilities operate on transient buffers/lists.

Dependencies/integration: used by parser, coordinator, client phase-2 creation, lock/fetch, and force code. Depends on RPC2, RVM, directory handles, ACL layout, volume quota metadata, and `rescomm`.

Risks/test signals: `AllocIncBSEntry` asserts on buffer overflow instead of returning an error. `CheckResRetCodes` uses `ntohl` where similar code uses `htonl`, which may affect logged addresses. `Dir_n_ACL` requires callers to `free` returned buffers. Test bounded buffer limits, duplicate inconsistency entries, host filtering for VNOVNODE, root quota packaging, and transaction cleanup on mark-inc failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resutil.cc -->
