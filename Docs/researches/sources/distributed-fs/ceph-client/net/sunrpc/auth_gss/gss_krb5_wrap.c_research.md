# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_wrap.c

## Purpose
`gss_krb5_wrap.c` implements Kerberos v2 wrap and unwrap token framing for privacy service. It inserts/removes RFC 4121 wrap headers, handles right-rotation count, delegates encryption/decryption to enctype callbacks, and reshapes `xdr_buf` contents so SUNRPC sees plaintext payloads.

## Important APIs, Types, and Functions
Buffer rotation helpers are `rotate_buf_a_little()`, `_rotate_left()`, and `rotate_left()`. `gss_krb5_wrap_v2()` creates a `KG2_TOK_WRAP` header with direction, acceptor-subkey, sealed flag, EC/RRC fields, and 64-bit sequence number, then calls the enctype encrypt callback. `gss_krb5_unwrap_v2()` validates header fields and direction, rotates ciphertext left if RRC is nonzero, calls the enctype decrypt callback, verifies the decrypted copy of the token header, removes header/confounder/trailer bytes, updates slack/alignment estimates, and returns a GSS status.

## Control Flow
Higher-level `auth_gss.c` privacy wrapping reserves RPCSEC_GSS framing, then calls generic `gss_wrap()`, which dispatches to `gss_krb5_wrap_v2()`. The unwrap path parses the opaque privacy blob, calls `gss_unwrap()`, and then reinitializes the XDR stream over the modified receive buffer. Encryption and decryption details are provided by `gss_krb5_crypto.c` via the selected enctype descriptor.

## State and Persistence
Wrap increments `seq_send64`. Unwrap mutates the `xdr_buf`: it can rotate data, memmove plaintext over the removed header area, shrink head length and total length, trim EC/checksum/trailer bytes, and set per-context slack/alignment outputs. No separate persistent state is stored in this file.

## Dependencies and Integration Points
It depends on XDR buffer subsegments, read/write helpers, Kerberos token constants, kernel time, and enctype-specific crypto callbacks. It is central to krb5p privacy service integration with RPC request/response buffers.

## Risks and Edge Cases
Unwrap must handle RRC rotation correctly or plaintext will be misaligned. Header verification compares the decrypted trailer header to the clear header, but ignores EC/RRC fields as expected. Buffer arithmetic uses `BUG_ON` to catch impossible memmove ranges. Sequence-number validation is left to RPCSEC_GSS callers, so that division of responsibility must remain intact.

## Test Signals
Primitive encryption and checksum behavior are covered by KUnit, but full wrap/unwrap token framing should be validated by krb5p integration tests over RPC calls, including nonzero RRC inputs and varied head/page/tail buffer layouts.
