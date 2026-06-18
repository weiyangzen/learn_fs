## sources/distributed-fs/openafs/src/rxgk/rxgk.h

### Purpose
`rxgk.h` is the public rxgk API header for creating client/server security objects, querying authenticated server connection state, managing rxgk keys, crypto operations, and token creation/printing.

### Important APIs, Types, And Functions
It defines `rxgk_getkey_func`, stats flags, security object constructors, `rxgk_GetServerInfo`, key management APIs, MIC/encrypt/decrypt helpers, transport-key derivation, nonce generation, enctype comparison, and token APIs such as `rxgk_make_token`, `rxgk_print_token`, and `rxgk_print_token_and_key`.

### Control Flow
No executable flow exists in the header. The declared functions form a layered API: key creation feeds token creation and security objects; security objects use packet crypto callbacks; server token extraction uses caller-supplied `getkey`.

### State, Persistence, And Dependencies
It includes generated comerr and protocol headers plus `rxgk_types.h`, `rx_opaque.h`, and `rx_identity.h`. State is opaque to callers through `rxgk_key` and `struct rx_securityClass`.

### Integration Points
Consumers are Rx clients/servers choosing `RX_SECIDX_GK`, token issuers/printers, and services that need authenticated identity/expiry. The functions are implemented across rxgk client, server, token, util, packet, and RFC3961 crypto files.

### Risks
Crypto APIs return rxgk wire-visible error codes, so backend errors must be translated. Callers must release `rxgk_key` and opaque buffers correctly. Public exposure of low-level crypto helpers increases misuse risk outside the intended security-object flow.

### Test Signals
API tests should create server and client security objects, issue/extract tokens, derive keys, verify MIC/encryption round trips, exercise enctype choices, and validate ownership rules for returned keys and opaque buffers.
