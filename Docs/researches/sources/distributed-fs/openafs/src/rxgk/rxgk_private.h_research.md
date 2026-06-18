## sources/distributed-fs/openafs/src/rxgk/rxgk_private.h

### Purpose
`rxgk_private.h` declares rxgk internal connection/object state, packet pseudoheader layout, statistics, and cross-file helper prototypes.

### Important APIs, Types, And Functions
Key structures are `rxgkStats`, packed `rxgk_header`, `rxgk_sprivate`, `rxgk_sconn`, `rxgk_cprivate`, and `rxgk_cconn`. Prototypes expose internal token extraction, security overhead calculation, key-number reconstruction, packet MIC/encrypt/check helpers, and enctype length lookup.

### Control Flow
The header has no executable flow. Its structures are filled by client/server security object callbacks and consumed by packet/crypto/token utilities.

### State, Persistence, And Dependencies
`rxgk_sconn` persists server connection authentication state, challenge nonce, expiry, identity, start time, key number, and token master key. `rxgk_cconn` persists client start time, key number, and stats. `rxgk_header` is explicitly packed for wire/pseudoheader crypto input.

### Integration Points
All rxgk implementation files include this header. It bridges public `rxgk.h` types with private Rx security callbacks.

### Risks
Packed layout must remain exactly compatible with the rxgk spec and crypto input. State fields such as `auth`, `challenge_valid`, and `key_number` are security sensitive and must be updated in the correct order. The comment typo `rgxk_server.c` is harmless but signals old experimental code.

### Test Signals
Static asserts or layout tests for `rxgk_header`, lifecycle tests for server/client connection state, and packet-authentication tests that mutate each pseudoheader field are valuable.
