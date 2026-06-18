<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/reptest.cc -->
# sources/distributed-fs/coda/coda-src/repair/reptest.cc

Purpose: small standalone test utility for repair directory-file serialization. It parses a repair description file, writes the parsed replica lists to `/tmp/xxx`, reads them back, and prints the reconstructed lines.

Important APIs/control flow: `main` calls `repair_parsefile(argv[1], &hcount, &harray)`, then `repair_putdfile("/tmp/xxx", hcount, harray)`, then `repair_getdfile("/tmp/xxx", &newhc, &newha)`. It iterates each `listhdr`, prints the `replicaId`, and prints each repair line through `repair_printline`.

State/persistence: global `harray`, `hcount`, and `repair_DebugFlag` support the repair parser/library linkage. The only persistent side effect is the fixed temporary file `/tmp/xxx`, which can collide across test runs and users.

Dependencies/integration: pulls in Coda base headers, RPC2, `vice.h`, and `repio.h`. It is not part of runtime repair flow; it is a parser/serializer smoke test for `repio` data structures.

Risks/test signals: no `argc` validation before `argv[1]`; the include line `<rpc2/rpc2.h> */` appears malformed and may only survive if this file is not regularly built. The fixed temp path is unsafe for concurrent tests. A useful test signal is round-tripping a multi-replica repair file with several operations and checking printed output equals the original semantic content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/reptest.cc -->
