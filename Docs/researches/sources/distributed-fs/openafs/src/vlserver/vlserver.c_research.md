## sources/distributed-fs/openafs/src/vlserver/vlserver.c

Purpose: executable entry point for the OpenAFS Volume Location server. It parses server/Rx/security/logging options, opens cell configuration, initializes Rx and Ubik, registers VLDB and RX statistics services, and starts the Rx server loop.

Important APIs/types/functions: global server state includes `vldb_confdir`, `VL_dbase`, `dynamic_statistics`, `rd_HostAddress`, `wr_HostAddress`, `lwps`, `smallMem`, `restrictedQueryLevel`, Rx tuning flags, and bind address state. `initialize_dstats()` resets dynamic opcode counters. `vldb_rxstat_userok()` gates RX stats administration to superusers. `vldb_IsLocalRealmMatch()` supplies audit user realm checks. `CheckSignal()` dumps name and id hash tables after initializing a read transaction; `CheckSignal_Signal()` bridges signal handling into pthread or LWP soft-signal paths. `main()` owns startup.

Control flow: startup initializes AFS paths, builds a `cmd` syntax, parses options, configures audit/logging, opens the server config dir, resolves the local host and VLDB server list, applies Rx bind/jumbo/MTU options, initializes Rx on `AFSCONF_VLDBPORT`, configures Ubik client/server security, sets `ubik_SyncWriterCacheProc = vlsynccache`, starts the Ubik database, initializes VLDB read/write address caches and stats, builds security classes, creates the VLDB service and RX stats service, applies dotted-principal policy, logs version/command line, sets the RX stats authorization callback, and calls `rx_StartServer(1)`.

State and persistence: this file does not directly mutate VLDB records, but it determines the persistent database path (`AFSDIR_SERVER_VLDB_FILEPATH` or `-database`) passed to Ubik and installs `vlsynccache()` so committed write-cache state is copied to read-cache state. It also opens audit and log destinations, and can bind to a restricted local interface based on NetInfo/NetRestrict.

Dependencies: OpenAFS command parser, directory path/config/auth/keys/audit/log utilities, Rx/RxKAD/Rx stats, Ubik, pthread soft signals or LWP soft signals, platform event/logging hooks, and generated `AFS_component_version_number.c`.

Integration points: `vlserver.c` wires generated Rx dispatchers (`VL_ExecuteRequest`, `RXSTATS_ExecuteRequest`) to the implementations in `vlprocs.c`. Ubik security callbacks use `afsconf_ClientAuth` or rxgk crypt based on `-s2scrypt`. Runtime options such as `-smallmem`, `-restricted_query`, `-allow-dotted-principals`, and `-rxbind` directly influence behavior in other VLDB modules.

Risks: startup failure paths often `exit()` after logging, so service managers see hard failures. Misconfigured `-rxbind`, NetInfo/NetRestrict, or host resolution can bind to an unintended address. `-noauth` changes the security posture for the whole service. Thread count is clamped only above `MAXLWP` and raised to at least four for the VLDB service. Signal-triggered hash dumping opens a transaction and can be noisy/expensive on large databases.

Test signals: cover option parsing conflicts (`-syslog` with `-logfile`/`-transarc-logs`), invalid `-restricted_query`, invalid `-s2scrypt`, Rx MTU rejection, `-p` clamping/minimum behavior, noauth and dotted-principal security configuration, bind host selection with mocked NetInfo/NetRestrict, Ubik init failure logging, and service registration using expected min/max procs.
