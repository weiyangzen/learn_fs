# sources/distributed-fs/ceph-client/net/ceph/auth_x.c

## Purpose
Implements the CephX authentication backend. It obtains and renews service tickets, builds encrypted authorizers, handles server challenges and replies, extracts session/connection secrets, and signs or verifies Ceph messages.

## Important APIs, Types, and Functions
The public initializer is `ceph_x_init()`. Backend ops include `ceph_x_is_authenticated()`, `ceph_x_should_authenticate()`, `ceph_x_build_request()`, `ceph_x_handle_reply()`, `ceph_x_create_authorizer()`, `ceph_x_update_authorizer()`, `ceph_x_add_authorizer_challenge()`, `ceph_x_verify_authorizer_reply()`, `ceph_x_invalidate_authorizer()`, `ceph_x_reset()`, `ceph_x_destroy()`, `ceph_x_sign_message()`, and `ceph_x_check_message_signature()`. Internal helpers manage ticket handlers in an rbtree (`get_ticket_handler()`, `process_one_ticket()`, `ceph_x_proc_ticket_reply()`), encryption wrappers (`ceph_x_encrypt()`, `ceph_x_decrypt()`), and authorizer buffers (`ceph_x_build_authorizer()`, `encrypt_authorizer()`).

## Control Flow
Initialization clones the client secret, prepares key usage transforms, sets `starting`, initializes the ticket-handler tree, and installs ops. The first monitor reply is a server challenge; the backend stores it and returns `-EAGAIN`. The next request either asks for an auth session key using the client secret and challenge-derived proof, or asks for principal service tickets using an AUTH authorizer. Ticket replies decrypt a "blob for me" into a session key and validity window, decode or decrypt the service ticket blob, update the handler, and set `have_keys`.

Service connections create a `ceph_x_authorizer` from the relevant service ticket: part A is clear metadata and ticket blob, part B is encrypted nonce/challenge data. A server challenge decrypts to a challenge value and causes the authorizer to be re-encrypted with `challenge+1`. The final reply decrypts `nonce+1` and optional connection secret; mismatch returns `-EPERM`. Message signing derives a 64-bit signature from encrypted or HMACed CRC/length blocks, with v1/v2 feature-dependent formats.

## State and Persistence
`struct ceph_x_info` holds the cloned client secret, start/challenge state, bitmask of service keys, an rbtree of `struct ceph_x_ticket_handler`, and a reusable AUTH authorizer. Each ticket handler owns a session key, ticket blob, secret id, expiration, and renewal time. Authorizers own cloned service session keys and `ceph_buffer` payloads. State is memory-only and destroyed by `ceph_x_destroy()`.

## Dependencies and Integration Points
Depends on `crypto.c` for AES/AES256KRB5 operations, `buffer.c` for ticket blobs, Ceph protocol encoders, Ceph feature bits, messenger message/footer layout, and generic auth callbacks. Key usage arrays must match `auth_x_protocol.h` constants and prepared crypto transform slots.

## Risks
CephX is sensitive to buffer offsets that differ between AES and AES256KRB5, key usage slot ordering, ticket expiration arithmetic, and zeroing decrypted secrets. `process_one_ticket()` updates handler state only after successful decode, but intermediate key material must be destroyed on errors. Signature behavior is disabled by `NOMSGSIGN`, so configuration can reduce integrity. Ticket-handler rbtree mutations assume caller holds `ac->mutex` through generic auth.

## Test Signals
Test initial challenge/request, auth ticket acquisition, service ticket acquisition, ticket renewal after `renew_after`, expiration clearing, malformed encrypted headers/magic, service challenge-response, nonce mismatch rejection, connection secret length limits and zeroing, message signing/checking with and without `CEPHX_V2`, AES and AES256KRB5 keys, authorizer update after secret-id change, and backend reset/destroy leak checks.
