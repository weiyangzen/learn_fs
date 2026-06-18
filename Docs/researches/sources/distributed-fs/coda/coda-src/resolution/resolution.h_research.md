<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resolution.h -->
# sources/distributed-fs/coda/coda-src/resolution/resolution.h

Purpose: small public header for resolution background server-check LWP entry points.

Important APIs: declares `ResCheckServerLWP(void *)` and `ResCheckServerLWP_worker(void *)` with C linkage for use by LWP/RPC initialization code and `rescomm` server failure handling.

State/persistence: no state. Implementations in `rescomm.cc` operate on transient server tables.

Dependencies/integration: included by `rescomm.h` and any code starting or signaling the server check LWPs.

Risks/test signals: C linkage keeps callback ABI simple, but there is no ownership or lifecycle declaration for the worker threads. Test startup initializes `ResCommInit` before these workers inspect server tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resolution.h -->
