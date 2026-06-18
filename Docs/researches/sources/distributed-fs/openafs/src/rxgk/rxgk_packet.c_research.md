## sources/distributed-fs/openafs/src/rxgk/rxgk_packet.c

### Purpose
`rxgk_packet.c` protects and validates Rx packets for rxgk AUTH and CRYPT levels by constructing a pseudoheader, applying MIC or encryption, and reversing those operations on receipt.

### Important APIs, Types, And Functions
Public internal APIs are `rxgk_mic_packet`, `rxgk_enc_packet`, and `rxgk_check_packet`. Static helpers populate the `rxgk_header`, verify MIC packets, and decrypt encrypted packets.

### Control Flow
For AUTH sends, the plaintext payload is prefixed in memory with a pseudoheader and MICed; the MIC is written into the reserved security header before the original payload. For CRYPT sends, the pseudoheader and payload are encrypted together and replace packet data. Receive-side AUTH extracts the MIC and payload, verifies against the pseudoheader, and shrinks packet data size. Receive-side CRYPT decrypts, validates the embedded pseudoheader in constant time, writes plaintext back, and restores plaintext data size.

### State, Persistence, And Dependencies
No persistent state is stored here. It uses Rx packet read/write and security header size APIs, `rxgk_key_number`, transport-key derivation, and RFC3961 wrappers. The 16-bit wire key number is stored in the Rx packet checksum field by caller code.

### Integration Points
Client and server security callbacks call `rxgk_check_packet` with role-specific key usages. `rxgk_util.c` must reserve matching header/trailer sizes before these routines run.

### Risks
Correct packet offsets depend on Rx security header size being set exactly for the security level. Contiguous encrypted/plain buffer lengths are bounded to 16-bit packet sizes. CRYPT relies on the encrypted pseudoheader to bind epoch, cid, call number, sequence, security index, and plaintext length. CLEAR ignores invalid key-number deltas by design.

### Test Signals
Tests should cover MIC and CRYPT round trips, tampered pseudoheader/data/MIC, wrong key usage, bad security header sizes, truncated MIC/ciphertext, ciphertext expansion near 65535 bytes, key-number increments/decrements, and CLEAR packet behavior.
