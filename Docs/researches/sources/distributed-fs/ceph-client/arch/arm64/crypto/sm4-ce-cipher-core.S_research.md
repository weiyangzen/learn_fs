## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-core.S

### Purpose
Implements the single-block SM4 cipher primitive using ARMv8 Crypto Extension `sm4e` instructions for the legacy `crypto_alg` cipher interface.

### Important APIs, Types, And Functions
Exports `sm4_ce_do_crypt(const u32 *rk, void *out, const void *in)`. It defines a local `sm4e` instruction macro and loads eight round-key vectors from the provided key schedule.

### Control Flow
The function loads one 16-byte input block, applies little-endian byte reversal when needed, loads the full key schedule in two vector batches, runs eight `sm4e` vector rounds, reverses the final word order, converts endian back on little-endian builds, stores the output, and returns.

### State, Persistence, And Dependencies
There is no internal state. The only effects are reading the caller's round-key and input buffers and writing the output block. Dependencies are `linux/linkage.h`, `asm/assembler.h`, ARM64 SM4 instruction support, and glue-side SIMD availability checks.

### Integration Points
Called by `sm4-ce-cipher-glue.c` for synchronous single-block `sm4` encryption and decryption. It uses the generic SM4 expanded keys produced by `sm4_expandkey()`.

### Risks
Because this is a minimal primitive, risks concentrate in endian conversion, key schedule ordering for decrypt versus encrypt, and executing the instruction on CPUs without SM4 support.

### Test Signals
Run SM4 ECB known-answer vectors through both `sm4` and `sm4-ce` driver names, compare encrypt/decrypt against generic `sm4_crypt_block`, and verify module loading only occurs with the SM4 CPU feature.
