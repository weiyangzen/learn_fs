# sources/distributed-fs/coda/coda-src/smon2/getvolinfo.c

Purpose: command-line RPC2 client that queries a Coda server for `ViceGetVolumeInfo` and prints decoded volume/replica mapping details.

Important functions: `Initialize` starts LWP and RPC2 with IPv6 option and 15-second timeout. `Bind` creates an unauthenticated RPC2 binding to host/port/subsystem. `viceaddr` converts stored server addresses to dotted IPv4 text. `main` parses optional `-p port`, resolves default `codasrv/udp`, binds to `SUBSYS_SRV`, calls `ViceGetVolumeInfo`, prints volume id/type, type ids, server count, eight replica/server pairs, and VSG address, then unbinds.

State/persistence: read-only network query; no local persistent writes.

Dependencies, risks, tests: depends on RPC2/LWP, `vice.h`, service lookup, and server availability. Risks include no null check if `coda_getservbyname` fails, IPv4-only address printing despite IPv6-enabled RPC options, fixed eight replica printout regardless `ServerCount`, and open-kimono security. Test default and explicit ports, missing service entry, nonexistent volume, replicated and nonreplicated volumes, and failed bind exit code.
