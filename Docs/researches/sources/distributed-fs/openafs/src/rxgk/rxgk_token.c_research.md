## sources/distributed-fs/openafs/src/rxgk/rxgk_token.c

### Purpose
`rxgk_token.c` creates, wraps, unwraps, decrypts, and extracts rxgk tokens and printed tokens.

### Important APIs, Types, And Functions
Public APIs are `rxgk_make_token`, `rxgk_print_token`, `rxgk_print_token_and_key`, and internal `rxgk_extract_token`. Static helpers map `RXGK_TokenInfo` to `RXGK_Token`, XDR-pack tokens and containers, encrypt/decrypt token blobs, unpack containers, and share common token creation logic.

### Control Flow
Token creation copies token info, inserts `K0` and identities, XDR-encodes the token, encrypts it with the service key using `RXGK_SERVER_ENC_TOKEN`, wraps it in `RXGK_TokenContainer` with kvno/enctype, and XDR-encodes the container. Extraction decodes the container, validates kvno/enctype, obtains the service key with `getkey`, decrypts the token blob, and XDR-decodes `RXGK_Token`.

### State, Persistence, And Dependencies
No global state exists. Outputs are caller-owned `rx_opaque` buffers or XDR-allocated token contents. Printed-token helpers generate random K0 bytes and return an `rxgk_key` for caller ownership. Dependencies include generated XDR rxgk types, `rx_opaque`, `opr_time`, and crypto helpers.

### Integration Points
Servers use `rxgk_extract_token()` during response verification. Token issuers use `rxgk_make_token()` for identity-bearing tokens and `rxgk_print_token*()` for printed tokens with empty identities and default lifetime/bytelife.

### Risks
`rxgk_make_token()` deliberately rejects empty identity lists to avoid accidental printed tokens. Printed tokens set expiration to `RXGK_NEVERDATE` and override lifetime/bytelife defaults. Error paths must avoid freeing caller-owned identity arrays while freeing XDR-owned token contents. `decrypt_token()` only accepts positive kvno/enctype values.

### Test Signals
Tests should round-trip normal and printed tokens, reject zero identities in `rxgk_make_token`, reject invalid kvno/enctype, simulate getkey/decrypt failures, verify default printed-token metadata, and run leak checks around XDR free paths.
