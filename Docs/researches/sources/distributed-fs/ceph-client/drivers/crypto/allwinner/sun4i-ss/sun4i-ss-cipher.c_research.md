<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c

## Purpose

`sun4i-ss-cipher.c` implements synchronous skcipher operations for the Allwinner sun4i Security System FIFO engine. It supports AES, DES, and 3DES in CBC and ECB modes, using software fallback for unsupported lengths or awkward scatterlists.

## Important APIs, Types, And Functions

The main data path is `sun4i_ss_cipher_poll()`, with a fast aligned path in `sun4i_ss_opti_poll()` and fallback path in `sun4i_ss_cipher_poll_fallback()`. Mode-specific exported callbacks include AES/DES/3DES CBC/ECB encrypt/decrypt functions. TFM lifecycle uses `sun4i_ss_cipher_init()` and `sun4i_ss_cipher_exit()`. Key setup is handled by `sun4i_ss_aes_setkey()`, `sun4i_ss_des_setkey()`, and `sun4i_ss_des3_setkey()`.

## Control Flow

Cipher requests validate non-empty SGs, reject non-block-multiple request lengths to fallback, and choose the optimized path when all source and destination SG offsets and lengths are 32-bit aligned. Hardware entry writes key registers, optional IV registers, and `SS_CTL`, streams input words into `SS_RXFIFO`, drains output from `SS_TXFIFO`, then clears the control register. CBC IV is updated from ciphertext on encryption or restored from the saved tail block on decryption.

## State And Persistence Behavior

TFM context stores key words, key length, key mode, hardware context, and fallback TFM. Request context stores mode, backup IV, and embedded fallback request. Device access is serialized with `ss->slock`; runtime PM is held for the TFM lifetime.

## Dependencies And Integration Points

It depends on skcipher API, scatterwalk/sg mapping iterators, DES key verification, runtime PM, SS register definitions, and algorithm templates registered by `sun4i-ss-core.c`.

## Risks And Test Signals

Risks include unaligned SG linearization bugs, IV corruption on in-place CBC decrypt, FIFO polling stalls, fallback flag propagation mistakes, and key material lifetime. Test with crypto manager vectors for AES/DES/3DES CBC/ECB, unaligned SGs, in-place and out-of-place requests, zero length, non-block-multiple fallback, and runtime PM cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c -->
