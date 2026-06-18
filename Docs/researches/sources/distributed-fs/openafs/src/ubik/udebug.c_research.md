
# sources/distributed-fs/openafs/src/ubik/udebug.c

`udebug.c` is the standalone Ubik diagnostic client. It contacts a server's VOTE service, fetches global and per-peer debug structures, and prints election, recovery, lock, transaction, version, and peer status in human-readable form.

Important functions are `PortNumber`, `PortName`, `CommandProc`, and `main`. `PortName` maps service names like `vlserver`, `ptserver`, `kaserver`, and `buserver` to default ports if service lookup fails. `CommandProc` resolves the target host and port, initializes Rx with null security, calls `VOTE_XDebug` with fallback to `VOTE_Debug` and old pre-3.5 `VOTE_DebugOld`, then optionally iterates `VOTE_XSDebug`/`VOTE_SDebug`/old equivalents for peer details.

Control flow is probe-and-print. After fetching `struct ubik_debug`, it compares remote and local clocks, warns when skew exceeds `MAXSKEW`, prints last yes vote and sync-site lease information, displays local and sync-site db versions, lock counts, active transaction tid, recovery flags, and for `-long` or sync sites prints each peer's addresses, clone flag, remote db version, last vote/beacon timing, and current/up/beaconSince state.

There is no persistent state. Dependencies are Rx client APIs, command parser `cmd`, host utilities, Ubik generated VOTE stubs, and structures from `ubik_int.h`. The tool intentionally uses null security because debug RPCs are informational.

Risks are diagnostic accuracy and compatibility: old server fallback uses struct casts, printed times depend on local clock comparison, and single-server sync-site state is fudged locally because voting is skipped for one server. Test signals include probing modern and old servers, named and numeric ports, localhost default, clone reporting, skew warning, and `-long` peer iteration termination.
