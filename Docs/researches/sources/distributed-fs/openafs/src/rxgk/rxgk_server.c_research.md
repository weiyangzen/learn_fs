## sources/distributed-fs/openafs/src/rxgk/rxgk_server.c

### Purpose
`rxgk_server.c` implements server-side rxgk security class callbacks for challenge generation, response verification, token extraction, authenticated identity storage, packet protection/checking, stats, and connection teardown.

### Important APIs, Types, And Functions
The exported APIs are `rxgk_NewServerSecurityObject()` and `rxgk_GetServerInfo()`. Static callbacks populate `rxgk_server_ops`: close, new connection, prepare packet, check authentication, create/get challenge, check response, check packet, destroy connection, and stats. Helpers handle no-auth reset, expiry checks, challenge reads, token processing, identity conversion, authenticator decryption, and constant-time authenticator checks.

### Control Flow
New server connections start unauthenticated with invalid placeholder level/expiry. Challenge creation generates and stores a random nonce; `GetChallenge` XDR-encodes it into the packet. `CheckResponse` decodes the response, decrypts/extracts the token using the configured `getkey`, checks expiry, stores the client start time, decrypts the authenticator with the derived transport key, validates nonce/level/epoch/cid/call vector length, reserves security overhead, imports call numbers, and marks the connection authenticated.

### State, Persistence, And Dependencies
Server object state is `rxgk_sprivate` with key callback and rock. Per-connection `rxgk_sconn` stores auth state, challenge, expiry, identity, stats, start time, key number, and `k0`. Dependencies include Rx security APIs, generated XDR rxgk types, `rx_identity`, `opr_time64`, packet helpers, token helpers, and RFC3961 wrappers.

### Integration Points
Rx invokes these callbacks for server authentication and packet handling. Application code can call `rxgk_GetServerInfo()` after authentication to obtain level, expiry, and a copied remote identity.

### Risks
Response decoding assumes contiguous packet data. On any response failure, `sconn_set_noauth()` clears key/identity and invalidates auth. Compound identities are not supported. Token lifetime/bytelife are parsed but ignored for rekeying. Constant-time comparison protects only selected authenticator fields; appdata is ignored.

### Test Signals
Tests should cover successful challenge-response, bad nonce/epoch/cid/level, expired tokens, getkey failures, malformed token containers, identity kinds and compound rejection, packet checks before auth, stats flags, key-number updates, and `rxgk_GetServerInfo()` ownership.
