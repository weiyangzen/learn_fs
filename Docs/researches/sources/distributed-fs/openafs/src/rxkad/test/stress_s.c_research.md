# sources/distributed-fs/openafs/src/rxkad/test/stress_s.c

Purpose: Server-side implementation for the rxkad stress RPC service.

Important APIs/functions: `GetKey` returns a static service key or reads an AFS keyfile and selects a kvno. `rxkst_StartServer` creates rxnull and rxkad server security classes and starts the Rx service. `CheckAuth` verifies security class, minimum auth level, and consistent authenticated client identity. RPC handlers implement `Kill`, `Fast`, `Slow`, and `Copious`.

Control flow and state: Server startup installs `minAuth`, configures service min/max procs, and donates the startup thread to `rx_StartServer`. `CheckAuth` caches the first rxkad client identity and requires later calls to match. `Copious` reads a requested byte stream, checks sum, writes a generated stream, and returns output sum. A small free list reuses 10KB buffers.

Dependencies and integration: Uses rxnull/rxkad server constructors, generated stress RPC executor, AFS keyfile structures, Rx call APIs, and stress error codes.

Risks: `Kill` intentionally finalizes and exits the process. Static identity cache and buffer free list are process-global. Keyfile parsing reads the whole legacy key structure and assumes expected layout.

Test signals: Provides server behavior used by load, auth, call replay, hijack, and stop-server client tests.
