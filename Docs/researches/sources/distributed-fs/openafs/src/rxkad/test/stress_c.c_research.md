# sources/distributed-fs/openafs/src/rxkad/test/stress_c.c

Purpose: Client-side implementation for rxkad stress tests, including load generation, generated-ticket setup, real-token setup, call-number replay tests, and packet hijack tests.

Important APIs/functions: `GetToken` retrieves existing AFS tokens; `GetTicket` creates a test v4-style ticket. `Copious`, `DoClient`, `RunLoadTest`, and `RepeatLoadTest` perform fast, slow, and large streaming RPCs over multiple worker threads/LWPs. `RunCallTest` manipulates call-number vectors to verify replay detection and v2 challenge call-number synchronization. `RunHijackTest` installs Rx packet hooks to zero or mutate packet checksums and redirect challenges between connections. `rxkst_StartClient` wires security objects, runs requested tests, prints stats, finalizes Rx, and exits.

Control flow and state: Worker structs track concurrent call exit codes. Multi-channel tests track per-channel call numbers. Hijack tests use global incoming/outgoing operation structs and Rx hooks `rx_justReceived` and `rx_almostSent` to observe or alter packets.

Dependencies and integration: Uses rxkad client constructors, ticket creation, DES random-key helpers, generated stress RPC stubs, Rx internal packet/call-number APIs, and auth token APIs.

Risks: Tests intentionally create broken client behavior and manipulate Rx internals. Hooks must be cleared after hijack tests. Generated tickets use a static test service key unless `-usetokens` is selected.

Test signals: Strong coverage for replay prevention, checksum downgrade detection, checksum tamper detection, challenge-oracle prevention, concurrent channel behavior, streaming integrity, and load timing.
