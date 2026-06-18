<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.h

Purpose: public communication-management interface and class declarations for the resolution subsystem.

Important APIs/types: declares group/server lifecycle functions (`GetResMgroup`, `PutResMgroup`, `ResCommInit`, `FindServer`, `GetServer`, `PutServer`), debug printers, `ViceResolve`, and `GetConnectionInfo`. `srvent` models one server and exposes connection/error/state methods. `RepResCommCtxt` holds handles, hosts, retcodes, primary host, multicast info, and dying flags. `res_mgrpent` models a resolution mgroup and exposes membership and result checks. `conninfo` stores inbound RPC peer information.

State/persistence: defines static transient tables for servers, resolution groups, and connection infos; no persistent storage.

Dependencies/integration: includes RPC2, Coda lists, `vice.h`, `res.h`, `vcrcommon.h`, `resutil.h`, and `resolution.h`. Many implementation details are friend-linked to iterators and server-check worker functions.

Risks/test signals: broad friend access and mutable arrays make invariants informal. `ALL_VSGS` is a static header variable, producing one copy per translation unit. Test all public printers and iterator filters, plus lifecycle balance for group leases and server references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.h -->
