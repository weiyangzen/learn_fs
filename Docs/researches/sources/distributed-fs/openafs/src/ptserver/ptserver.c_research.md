# sources/distributed-fs/openafs/src/ptserver/ptserver.c research

## Purpose
`ptserver.c` is the daemon entry point for the OpenAFS Protection Server. It parses server options, initializes logging/auditing/configuration, sets global ptserver policy, initializes Rx and Ubik, registers the Protection Server and RX statistics services, and starts the Rx server loop.

## Important APIs, types, and functions
Global daemon state includes `cheader`, `dbase`, `prdir`, `restricted`, `restrict_anonymous`, `rxMaxMTU`, `rxBind`, `rxkadDisableDotCheck`, and optional `depthsg`. `prp_access_mask` parses textual default access masks into `PRP_*` bits. `pr_rxstat_userok` authorizes RX statistics management via `afsconf_SuperUser`. `pr_IsLocalRealmMatch` adapts `afsconf_IsLocalRealmMatch` for audit user checks.

The `main` function owns all runtime setup: directory initialization, option registration and parsing, default access parsing, supergroup depth, restriction flags, audit options, database path, thread count bounds, syslog/file log setup, Rx stats toggles, Rx bind/max-MTU options, rxkad dotted principal behavior, rxgk server-to-server crypt selection, config open, host/server discovery, Ubik security procedure setup, Rx initialization, Ubik server initialization, security object construction, service registration, and `rx_StartServer`.

## Control flow, state, and persistence
The daemon starts by validating OpenAFS server paths and defaulting the protection database and config directory. It applies CLI/config options before opening audit and log outputs. It opens the server config dir into global `prdir`, determines whether `NoAuth` is present, discovers the local host and protection server cell info, and sets audit local-realm callbacks.

Ubik is configured with client and server security procedures, then initialized with `ubik_ServerInitByInfo` using the protection database path. The persistent protection database itself is managed by Ubik and initialized lazily by `Initdb` in `ptutils.c` when RPCs begin transactions. `ubik_nBuffers` is increased to handle worst-case delete transactions involving continuation blocks and reciprocal membership cleanup. With `SUPERGROUPS`, `pt_hook_write` is installed after Ubik initialization to invalidate supergroup maps when group records are written.

## Dependencies and integration points
This file integrates AFS directory/path initialization, OpenAFS command parsing, logging, audit, Rx, Rx stats, Rx security classes, rxkad/rxgk configuration, Ubik replication, `afsconf` cell/server data, and generated `PR_ExecuteRequest`. It owns the global variables consumed by `ptprocs.c` and `ptutils.c`.

## Risks and test signals
Startup option interactions are the main risk: `-syslog` versus `-logfile`/`-transarc-logs`, thread bounds, invalid `-s2scrypt`, invalid `-default_access`, bad config directories, and Rx bind/netinfo behavior must fail clearly. Security-sensitive tests should cover noauth mode, restricted mode, anonymous restriction, dotted principal toggles, rxgk server-to-server crypt configuration, and RX stats authorization. Database safety depends on structure-size checks under `SUPERGROUPS`, correct `ubik_nBuffers`, and successful Ubik initialization before the service accepts requests.
