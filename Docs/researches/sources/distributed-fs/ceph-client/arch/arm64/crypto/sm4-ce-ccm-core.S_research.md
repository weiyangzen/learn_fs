## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-core.S

### Purpose
Implements ARMv8 SM4 Crypto Extension assembly for CCM mode payload encryption/decryption, CBC-MAC updates, and final tag encryption.

### Important APIs, Types, And Functions
Exports `sm4_ce_cbcmac_update`, `sm4_ce_ccm_final`, `sm4_ce_ccm_enc`, and `sm4_ce_ccm_dec`. Important macros are `inc_le128`, `SM4_PREPARE`, `SM4_CRYPT_BLK`, and `SM4_CRYPT_BLK2`; `RMAC` holds the CBC-MAC accumulator.

### Control Flow
`sm4_ce_cbcmac_update` encrypts the current MAC and XORs full AAD/message blocks. `sm4_ce_ccm_enc` advances CTR values, encrypts plaintext with CTR keystream, and folds plaintext into the MAC. `sm4_ce_ccm_dec` decrypts ciphertext then folds recovered plaintext into the MAC. Tail loops operate byte-by-byte, updating the saved MAC buffer. `sm4_ce_ccm_final` encrypts both MAC and CTR0 and XORs them to produce the tag.

### State, Persistence, And Dependencies
State is caller-owned: round keys, CTR/IV buffer, MAC buffer, source, and destination. Full-block paths update CTR and MAC; byte-tail paths write partial MAC bytes in place. Dependencies include `sm4-ce-asm.h`, `asm/assembler.h`, linkage/CFI types, and SIMD protection by C glue.

### Integration Points
Called only by `sm4-ce-ccm-glue.c`, which formats CCM B0/AAD, validates auth size, and walks scatterlists.

### Risks
Tail MAC byte writes, CTR carry/endian behavior, and encrypt-vs-decrypt MAC input selection are subtle. A mismatch with `ccm_format_input()` or walk tail decisions can produce invalid tags or plaintext corruption.

### Test Signals
Run RFC8998/NIST CCM vectors for SM4, AAD-only and payload-only requests, message lengths crossing 15/16/17/63/64 bytes, odd auth sizes rejection, decrypt tag failure, and segmented scatterlists.
