## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-asm.h

### Purpose
Supplies reusable ARMv8 SM4 Crypto Extension assembly macros for one, two, four, and eight block transforms.

### Important APIs, Types, And Functions
Macro surface includes `SM4_PREPARE`, `SM4_CRYPT_BLK_BE`, `SM4_CRYPT_BLK`, `SM4_CRYPT_BLK2_BE`, `SM4_CRYPT_BLK2`, `SM4_CRYPT_BLK4_BE`, `SM4_CRYPT_BLK4`, `SM4_CRYPT_BLK8_BE`, and `SM4_CRYPT_BLK8`. The macros assume the including file defines the `sm4e` instruction macro and uses v24-v31 for expanded round keys.

### Control Flow
Including assembly files call `SM4_PREPARE(ptr)` to load eight 128-bit round-key vectors, then invoke the block macros inside mode-specific loops. The macros perform required endian conversion, issue the SM4 round instruction for every round-key vector, then reverse the final word order into the kernel's block layout.

### State, Persistence, And Dependencies
No standalone state or object code is generated. The macros only affect registers and caller buffers when expanded by assembly sources such as SM4 CE core, CCM, and GCM. Dependencies are ARMv8 SM4 Crypto Extension instruction encodings and consistent vector register allocation.

### Integration Points
Included by `sm4-ce-core.S`, `sm4-ce-ccm-core.S`, and `sm4-ce-gcm-core.S` to keep SM4 block logic consistent across modes.

### Risks
Macro register assumptions are global and fragile; a caller reusing v24-v31 or omitting endian preparation can silently corrupt output. Any SM4 round-order bug affects every CE mode.

### Test Signals
Cross-build all including assembly files; run SM4 ECB/CBC/CTR/XTS/CCM/GCM known-answer tests; disassemble to confirm expected `sm4e` instruction encodings and no accidental register overlap.
