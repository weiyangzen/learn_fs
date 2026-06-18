# sources/distributed-fs/openafs/src/lwp/test/selclient.c

Purpose: client-side IOMGR select test, especially for read/write/exception fd sets with descriptors above 31 and TCP out-of-band behavior.

Important APIs/types/functions: parses options `-fd`, `-oob`, `-soob`, `-delay`, `-end`, and `-write`. Uses `sendTest` for write/echo verification and `sendEnd` to request server termination. Uses helpers from `selsubs.c` and protocol structure from `seltest.h`.

Control flow: `main` opens enough dummy descriptors to force the socket to a requested number, connects to the server, and either sends an end command, sends OOB data, or initializes IOMGR and runs `sendTest`. `sendTest` sends an `SC_WRITE` command, writes a deterministic byte pattern, optionally one byte at a time through `IOMGR_Select` on writable/exception sets, reads the echo, and compares buffers.

State and persistence: uses transient socket state, allocated buffers, and optional signal count `nSigIO`. No persistent files.

Dependencies/integration: depends on sockets, `IOMGR_Initialize`, `IOMGR_Select`, `IOMGR_AllocFDSet`, and common select-test helpers.

Risks and test signals: assumes blocking socket behavior and timing appropriate to the host/network; loopback may require longer delays. Assertions validate fd set cleanup, write progress, and echoed data integrity.
