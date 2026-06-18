# sources/distributed-fs/openafs/src/rx/simple.example/Makefile.in

## Purpose
Builds the simple RX example client/server and generated RX stubs.

## Important APIs, Types, And Functions
Targets include `all`, `sample_client`, `sample_server`, generated `sample.cs.c`, `sample.ss.c`, `sample.h`, and `clean`. It includes `Makefile.config` and `Makefile.pthread`, uses `RXGEN`, links `libafsauthent.a`, `libafsrpc.a`, `util.a`, crypto/roken libraries, and `XLIBS`. Comments show an alternate LWP RX library setup.

## Control Flow
`all` builds client and server. RXGEN generates client stubs with `-C`, server stubs with `-S`, and the header with `-h` from `sample.xg`. Object dependencies ensure generated header availability. Link rules combine local objects, generated stubs, and RX/auth libraries.

## State And Persistence
Generated C/header files, object files, and binaries are build artifacts. `clean` removes objects, generated stubs, and binaries.

## Dependencies And Integration Points
This makefile integrates RXGEN-generated RPC code with the pthread RX library stack and the simple example sources. It depends on top-level OpenAFS build variables and libraries.

## Risks And Test Signals
Risks include stale generated files, wrong thread flavor if switching between pthread/LWP comments, and missing library ordering. Successful `make` in the example directory and a client/server add/subtract run are the primary signals.
