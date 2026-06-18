# sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.h

Purpose: defines the private register map, control bits, mode/direction constants, timeout value, and per-TFM context for the AMD Geode LX AES driver.

Important APIs and control flow: mode constants identify ECB and CBC, direction constants distinguish encrypt and decrypt, and register offsets name control, interrupt, source, destination, length, write-key, and write-IV registers. Control bits start an operation, select encryption, request key write, set coherent source/destination access, and enable CBC. Interrupt bits identify pending AES channel events and clear/mask state. `AES_OP_TIMEOUT` bounds the driver's polling loop. `struct geode_aes_tfm_ctx` stores the hardware AES-128 key, either a fallback `crypto_skcipher` or legacy `crypto_cipher`, and the active key length.

State and persistence behavior: the header itself has no runtime state. It defines how `geode-aes.c` persists per-TFM key/fallback state and how MMIO offsets are interpreted. The hardware key and IV registers are transient and rewritten for each operation.

Dependencies and integration points: depends on AES key-size constants and Crypto API fallback types included by the C file. Its register constants are consumed directly by MMIO reads/writes and must match the AMD LX AES BAR layout.

Risks and test signals: risks include incorrect register constants causing data corruption, timeout tuning hiding hung hardware or false failures, an unused hidden-key flag, and context union misuse if cipher and skcipher init paths are mixed. Test signals include compile coverage for both legacy cipher and skcipher users, register access traces on known hardware, fallback allocation and free for both union variants, and AES-128 hardware results matching software for ECB and CBC.
