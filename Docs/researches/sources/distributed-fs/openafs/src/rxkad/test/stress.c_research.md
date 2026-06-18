# sources/distributed-fs/openafs/src/rxkad/test/stress.c

Purpose: Command-line driver for the rxkad stress test, starting server and/or client roles and translating options into shared parameter structs.

Important APIs/functions: `StringToAuth` parses authentication names into rxkad levels or unauthenticated mode. `CommandProc` handles all command options, starts server worker via pthread or LWP, configures client load/call/hijack/repeat/timing/token options, initializes Rx, and starts the client. `main` builds the command syntax.

Control flow and state: Defaults to combined local server and client if neither role is specified. Server parameters include thread count, minimum auth, trace, and keyfile. Client parameters include target server, call counts, transfer sizes, auth level, repeat behavior, max skew, token use, cell, and stop-server behavior.

Dependencies and integration: Uses OpenAFS command parser, Rx, rxkad, LWP/pthread abstractions, stress RPC generated headers, and globals such as `rxi_2dchoice`.

Risks: Many options mutate global Rx behavior. Some compatibility options are retained but ignored. Combined server/client mode depends on thread/LWP scheduling.

Test signals: This is the entrypoint for load, call-number replay, checksum hijack, timing, and server shutdown test modes.
