# sources/distributed-fs/openafs/src/kauth/kaserver.c

## Purpose
Bootstraps and runs the deprecated OpenAFS KA authentication server. It parses command-line configuration, opens cell/server configuration, initializes Ubik and Rx services, starts the KA RPC services, initializes procedure/database state, and optionally enables the old UDP interface.

## Important APIs, Types, And Functions
Important functions are `KA_rxstat_userok`, `KA_IsLocalRealmMatch`, `es_Report`, `initialize_dstats`, `convert_cell_to_ubik`, `kvno_admin_key`, and `main`. Global server state includes `dynamic_statistics`, `KA_dbase`, `myHost`, `verbose_track`, `krb4_cross`, `rxBind`, `SHostAddrs`, `KA_conf`, `MinHours`, and `npwSums`.

## Control Flow
`main` initializes audit and server paths, parses options for database/local paths, noauth, fast keys, dbfixup, cellservdb, security level, crossrealm, rxbind, minhours, and rxstats. It opens KA cell config, logging, emits a deprecation warning, derives or parses the Ubik server list, configures audit user checks, sets Ubik client/server security procs, binds Rx, starts Ubik, creates authentication, ticket-granting, maintenance, and rxstats services, initializes dynamic stats, allows rxstat management by superusers, starts Rx server processing, initializes `kaprocs`, starts legacy UDP access if possible, and donates the main LWP to `rx_ServerProc`.

## State And Persistence
Persistent state includes the Ubik KA database at `dbpath`, local auxiliary files at `lclpath`, server logs, and optional audit logs. Runtime global state configures security, cell config, statistics, server address binding, and rxkad key lookup.

## Dependencies And Integration Points
It integrates afsconf cell/security config, Ubik replication, Rx/rxkad services, audit, server logging, `kadatabase.c`, `kaprocs.c`, `kalog.c`, and `krb_udp.c`. The maintenance service uses rxkad with `kvno_admin_key`, which consults the in-memory key cache only.

## Risks And Test Signals
Risks include running a deprecated DES-based auth server, `-noAuth`, clear Ubik security level, old UDP service exposure, address-selection/bind mistakes, command-line parsing by prefix, and reliance on single-thread KA service max procs. Test signals include startup with CellServDB and explicit servers, rxbind/netinfo behavior, Ubik quorum formation, service registration IDs, noauth and crossrealm flags, audit/log file creation, rxstats authorization, and clean failure on missing paths or config.
