# sources/distributed-fs/ceph-client/fs/smb/client/smb2transport.c

## Purpose
`smb2transport.c` implements SMB2/SMB3 request signing, signature verification support, session/channel signing key lookup, SMB3 key derivation, mid-queue allocation/setup, receive checking, and AEAD crypto transform allocation. It bridges built SMB2 PDUs to transport machinery that assigns message IDs, tracks pending requests, signs outgoing messages, and validates incoming responses.

## Important APIs, Types, And Functions
Exported functions include `generate_smb30signingkey`, `generate_smb311signingkey`, `smb2_verify_signature`, `smb2_check_receive`, `smb2_setup_request`, `smb2_setup_async_request`, `smb2_find_smb_tcon`, and `smb3_crypto_aead_allocate`. Internal helpers include `smb3_get_sign_key`, `smb2_find_smb_ses_unlocked`, `smb2_get_sign_key`, `smb2_find_smb_sess_tcon_unlocked`, `smb2_calc_signature`, `generate_key`, `generate_smb3signingkey`, `smb3_calc_signature`, `smb2_sign_rqst`, `smb2_seq_num_into_buf`, `smb2_mid_entry_alloc`, and `smb2_get_mid_entry`.

## Control Flow
Outgoing synchronous requests call `smb2_setup_request`: assign a message ID with credit-charge aware sequencing, validate server/session status, allocate and queue a MID, and sign if required. Async requests use `smb2_setup_async_request`, which performs a lighter negotiation-status check, allocates a MID, and signs before submission. If signing fails, message IDs are reverted and MIDs are deleted or released.

SMB2 signing uses HMAC-SHA256 with the NTLMv2 session key. SMB3 signing uses AES-CMAC and channel-specific signing keys. Both zero the signature field before calculation and handle an RFC1002 length vector before signing the data vectors. SMB3 key derivation uses dialect-specific KDF labels and contexts, with SMB3.1.1 using the preauth hash and AES-256 using the full session key for encryption/decryption KDF input.

## State And Persistence Behavior
The file mutates server sequence numbers, pending MID queues, MID refcounts/states, session and channel signing keys, session encryption/decryption keys, server AEAD encrypt/decrypt handles, and credit-related MID fields. It takes `cifs_tcp_ses_lock`, `ses_lock`, `chan_lock`, `srv_lock`, and `mid_queue_lock` around shared state.

## Dependencies And Integration Points
It depends on CIFS globals/debug helpers, SMB2 prototype/status definitions, Linux crypto HMAC/AES-CMAC/AEAD APIs, the mid mempool, tracepoints, and error helpers. `smb2pdu.c` relies on this file through request setup and AEAD allocation; lower send paths rely on the prepared MIDs and signatures.

## Risks
Key lookup across multichannel is concurrency-sensitive. Signing must preserve RFC1002/vector handling rules or fail under specific send paths. Message ID rollback on failures must match MID queue state. AEAD allocation failure paths must avoid leaking half-created transforms. Debug key dumping is gated but sensitive.

## Test Signals
Signed and unsigned mounts, SMB2.1 HMAC signing, SMB3 AES-CMAC signing, multichannel binding/reconnect, SMB3.1.1 preauth key derivation, AES-256 negotiation, signature-failure injection, MID allocation failure injection, and crypto allocation failure injection are key signals.
