## sources/distributed-fs/openafs/src/rxkad/crypt_conn.c

### Purpose
`crypt_conn.c` provides packet encryption/decryption routines for the rxkad security object using the `rx_data()` fragment accessor path.

### Important APIs, Types, And Functions
It defines `rxkad_DecryptPacket()` and `rxkad_EncryptPacket()` for `XPRT_RXKAD_CRYPT`. Both call `fc_cbc_encrypt()` with either `FCRYPT_DECRYPT` or `FCRYPT_ENCRYPT`.

### Control Flow
Each function copies the caller IV into a local XOR vector, records byte stats using the security object's private type, then iterates packet data fragments by index. For encryption it writes zero into the second 32-bit word of the packet security header before CBC processing. Each loop processes the minimum of remaining length and fragment length.

### State, Persistence, And Dependencies
No local persistent state exists. Packet contents are mutated in place. Dependencies include Rx packet APIs, rxkad stats, `private_data.h`, and fcrypt key schedule/IV types.

### Integration Points
rxkad uses these functions behind packet processing callbacks for crypt-level connections. This file is separate from `bg-fcrypt.c`'s wirevec implementation, reflecting alternate platform/build paths.

### Risks
The loop breaks silently if `rx_data()` returns no data before `len` reaches zero, yet still returns success. Integrity checksum code is commented out, so the security header checksum word is always zero. Fragment alignment and block-size assumptions are delegated to fcrypt.

### Test Signals
Tests should include multi-fragment packets, early missing-fragment cases, partial final lengths, stats increments, header zeroing, and encrypt/decrypt round trips compared with `bg-fcrypt` behavior.
