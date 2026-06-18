# sources/distributed-fs/coda/coda-src/smon2/rpc2ping.c

Purpose: simple health-check utility that verifies an RPC2 binding can be established to a Coda server.

Important functions: `Initialize` initializes LWP/RPC2 with IPv6 option and timeout; `Bind` creates an unauthenticated binding to host/port/subsystem; `main` parses optional `-p port`, otherwise uses `codasrv/udp` and `SUBSYS_SRV` numeric id, attempts bind/unbind, prints success or failure, and exits `0` on success, `2` on critical bind failure, `1` on usage error.

State/persistence: no persistent state; network-only probe.

Dependencies, risks, tests: depends on RPC2, LWP, service lookup, and DNS. It only detects bindability, not application-level server health. Risks include no check for missing service lookup, fixed subsystem id literal, and unauthenticated open binding. Test success/failure exit codes, explicit port, DNS failure, server down, and monitoring integration expecting Nagios-style critical code 2.
