## sources/distributed-fs/openafs/src/vol/daemon_com.c

Purpose: localhost synchronous command/response transport used by volume-related daemons and clients, currently over Unix-domain sockets when available or loopback TCP otherwise.

Important APIs/types/functions: client helpers include `SYNC_getAddr()`, `SYNC_getSock()`, `SYNC_connect()`, `SYNC_disconnect()`, `SYNC_closeChannel()`, `SYNC_reconnect()`, `SYNC_ask()`, and internal `SYNC_ask_internal()`. Server helpers include `SYNC_getCom()`, `SYNC_putRes()`, `SYNC_verifyProtocolString()`, `SYNC_cleanupSock()`, and `SYNC_bindSock()`. Globals include callback hook `V_BreakVolumeCallbacks`; constants include `MAXHANDLERS`, `MAX_BIND_TRIES`, and `AFS_SOCKADDR_LEN`.

Control flow: clients lazily connect, retry connection with a fixed backoff sequence, stamp outgoing command headers with protocol version, sequence numbers, pid/tid, and DAFS flags, write the command, optionally short-circuit channel close, then read and validate a response header/payload. `SYNC_ask()` wraps the low-level exchange with retry/reconnect behavior until retry count or hard timeout is exceeded. Servers read command headers and optional payloads with `readv`/`recv`, validate lengths, fill response headers with protocol version and sequence numbers, serialize response header/payload, and write it back. Binding configures `SO_REUSEADDR`, retries bind, and listens.

State and persistence: client state persists socket descriptor, endpoint, protocol version, sequence counters, retry/hard-timeout policy, and protocol name. Server state persists listening socket, endpoint address, protocol version, sequence counters, bind retry limit, and listen depth. Filesystem persistence is limited to Unix socket path creation/removal under the server local directory.

Dependencies: socket APIs (`socket`, `connect`, `bind`, `listen`, `send`/`recv` or `write`/`readv`), Unix socket path utilities, OpenAFS endpoint/protocol structures from `daemon_com.h`, LWP/pthread thread id helpers, `FT_ApproxTime`, logging from `common.c`, and platform abstractions such as `rk_closesocket` and `osi_socket`.

Integration points: shared by fileserver, volserver, salvageserver, salvager, FSSYNC, and SALVSYNC style local coordination. Protocol mismatch logs explicitly tell operators to keep fileserver, volserver, salvageserver, and salvager on the same version.

Risks: assumes full writes/reads for command and response sizes; partial socket I/O is treated as failure rather than looped. Connection setup can sleep for a long backoff sequence. Some error handling has duplicate unreachable statements. `SYNC_getSock()` uses `opr_Verify` and aborts on socket creation failure. Unix socket paths are formatted into fixed `sun_path`. Protocol length fields must be correct, or peers return `SYNC_COM_ERROR`.

Test signals: client/server loopback exchanges with and without payloads, channel close behavior, protocol mismatch `SYNC_BAD_COMMAND`, response too short/too long/bad length, retry/reconnect on dropped sockets, Unix and TCP endpoint address construction, bind retry and cleanup behavior, unterminated protocol string detection, sequence number increments, and partial I/O/error injection.
