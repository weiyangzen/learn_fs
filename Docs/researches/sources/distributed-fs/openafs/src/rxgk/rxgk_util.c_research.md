## sources/distributed-fs/openafs/src/rxgk/rxgk_util.c

### Purpose
`rxgk_util.c` provides common rxgk helpers for reserving per-packet security overhead and reconstructing full key numbers from truncated wire values.

### Important APIs, Types, And Functions
`rxgk_security_overhead()` sets Rx security header/trailer reservation for CLEAR, AUTH, and CRYPT levels. `rxgk_key_number()` maps a 16-bit packet checksum field and local 32-bit key number to the peer's effective 32-bit key number.

### Control Flow
Security overhead returns no reservation for CLEAR, reserves MIC length as header for AUTH, and reserves `rxgk_header` plus max crypto trailer expansion for CRYPT. Key-number reconstruction compares low 16 bits and accepts same, +1, or -1 deltas, rejecting wrap beyond 0 or `MAX_AFS_UINT32` and other jumps.

### State, Persistence, And Dependencies
The functions mutate only the given Rx connection's security size fields and caller-provided output key number. They depend on crypto helpers for MIC length and cipher overhead and on Rx packet/security APIs.

### Integration Points
Client/server new-connection and successful-authentication paths call `rxgk_security_overhead()` before packet processing. Packet receive paths use `rxgk_key_number()` before deriving transport keys.

### Risks
Incorrect overhead reservation breaks packet offsets in `rxgk_packet.c`. The key-number algorithm intentionally only allows one-step changes, so lost rekey synchronization yields `RXGK_BADKEYNO`. CLEAR connections ignore key-number errors higher up, but this helper still reports them.

### Test Signals
Tests should assert reserved sizes by level/enctype, invalid level handling, MIC length failures, cipher overhead failures, key number same/+1/-1 behavior, low-16-bit wrap cases, and out-of-range wrap rejections.
