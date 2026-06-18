<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S

Purpose: This 32-bit x86 assembly file implements single-block Twofish encryption and decryption. It is the i386 counterpart to the x86-64 single-block assembly and backs the base `twofish-asm` cipher driver on 32-bit builds.

Important APIs/types/functions: Public symbols are `twofish_enc_blk` and `twofish_dec_blk`. Macros define argument stack offsets, block word offsets, `struct twofish_ctx` table offsets, input/output whitening, `encrypt_round`, `encrypt_last_round`, `decrypt_round`, and `decrypt_last_round`.

Control flow: Encryption loads a 16-byte block, applies input whitening from context `w`, runs the Twofish round sequence using precomputed S-box tables and round keys, applies output whitening, and stores the block. Decryption performs the inverse order with the decryption round macros. The code uses 32-bit general registers and byte subregisters for table lookups.

State and persistence: No persistent state is owned. It reads the expanded Twofish context passed on the stack and writes the output block. Callee-saved register handling is part of the assembly routine's ABI.

Dependencies and integration points: It includes `linux/linkage.h` and `asm/asm-offsets.h`. It is linked with `twofish_glue.c`, which registers the Crypto API cipher and exports the symbols to multi-block modules.

Risks and test signals: Stack argument offsets and context table offsets are critical. Byte-register lookup code is sensitive to partial-register behavior and endianness. Tests should cover 32-bit build/link, Twofish known-answer vectors for all key lengths, unaligned source/destination, and module interactions with 3-way or AVX glue where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-i586-asm_32.S -->
