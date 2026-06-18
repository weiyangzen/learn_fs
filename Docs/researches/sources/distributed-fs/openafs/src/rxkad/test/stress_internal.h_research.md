# sources/distributed-fs/openafs/src/rxkad/test/stress_internal.h

Purpose: Shared private definitions for rxkad stress client/server sources.

Important APIs/types: Declares `serviceKey`, `serviceKeyVersion`, test principal constants, `serverParms`, `clientParms`, `rxkst_StartServer`, and compatibility `opaque` typedefs. It also defines a local `assert` macro and compatibility aliases for older Rx symbols.

Control flow and state: Header only. Parameter structs carry command-line configuration from `stress.c` into server/client implementations.

Dependencies and integration: Included by `stress.c`, `stress_c.c`, and `stress_s.c`; depends on generated `stress.h` and rxkad public types.

Risks: The local `assert` aborts the process and is always active. Constants hard-code test identities and cell names.

Test signals: Compile-time glue for every stress mode; incorrect struct fields would break command dispatch or auth setup.
