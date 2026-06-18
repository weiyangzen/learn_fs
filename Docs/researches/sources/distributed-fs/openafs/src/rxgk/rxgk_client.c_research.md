## sources/distributed-fs/openafs/src/rxgk/rxgk_client.c

### Purpose
`rxgk_client.c` implements the client-side Rx security class callbacks for rxgk, including per-connection setup, packet protection, challenge response construction, packet verification, stats, and security object lifetime.

### Important APIs, Types, And Functions
The exported constructor is `rxgk_NewClientSecurityObject()`. Static callbacks in `rxgk_client_ops` include close, new connection, prepare packet, get response, check packet, destroy connection, and stats. Helpers copy/destroy private state, fill `RXGK_Authenticator`, encrypt authenticators, and pack `RXGK_Response`.

### Control Flow
A new security object copies the token master key and token. A new connection records a safe start time, reserves security overhead, stores `rxgk_cconn`, and references the object. Packet preparation updates stats, writes the low 16 bits of key number into the packet checksum field, derives a transport key, and applies MIC or encryption for AUTH/CRYPT. Challenge response decodes server nonce, copies the token, fills channel-binding authenticator data, encrypts it, packs the response into the packet, and sets the wire key number.

### State, Persistence, And Dependencies
`rxgk_cprivate` persists per security object with `k0`, enctype, level, and token. `rxgk_cconn` persists per Rx connection with start time, key number, and stats. Dependencies include Rx packet APIs, XDR generated rxgk types, `rx_opaque`, RFC3961 wrappers through public rxgk functions, and `opr_time64`.

### Integration Points
Rx calls these callbacks during connection lifecycle, challenge/response authentication, send preparation, receive verification, and stats collection. The packet work delegates to `rxgk_packet.c`.

### Risks
Challenge decoding assumes contiguous packet payload. Rekey policy is only partially implemented; stats are not reset on key-number update. `cp->enctype` is stored but not used in the shown code. Security depends on correct call-number vector export and matching server-side authenticator checks.

### Test Signals
Tests should cover object creation/destruction, challenge-response round trip, AUTH and CRYPT packet protection, bad or truncated challenge packets, key-number wrap/update handling, stats increments, clear-level behavior, and allocation-failure cleanup.
