<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h

Purpose: defines CAAM descriptor command encodings, protocol IDs, algorithm selectors, scatter/gather bits, operation fields, math/jump/move fields, and protocol constants used by descriptor builders throughout the driver.

Important APIs and control flow: the file is macro-only. It establishes command opcodes (`CMD_KEY`, `CMD_LOAD`, `CMD_FIFO_STORE`, `CMD_OPERATION`, `CMD_JUMP`, etc.), descriptor header bits (`HDR_ONE`, length/share/start fields), key/load/store/fifo pointer formats, protocol IDs for IPsec, SRTP, MACsec, WiFi, WiMAX, SSL/TLS/DTLS, blob, DKP, RSA/DSA, algorithm selectors and AAIs for AES/DES/MDHA/RNG/SNOW/Kasumi/CRC/ChaCha/Poly1305/PKHA, sequence pointer flags, math source/destination encodings, jump tests, NFIFO entries, and frame descriptor command bits.

State and persistence behavior: none at runtime; these constants define the ABI between software-generated descriptor words and CAAM hardware. Any change affects every descriptor emitted by `desc_constr.h` and algorithm-specific descriptor builders.

Dependencies and integration points: consumed by controller RNG descriptors, crypto API descriptor constructors, PKC/RSA, QI shared descriptors, key split generation, and error decoding. It also sets `MAX_CAAM_DESCSIZE` and SG table flags that influence buffer sizing and DMA layout.

Risks and test signals: risks include silent hardware misprogramming from one-bit macro mistakes, legacy protocol constants for weak TLS/SSL/RC4/DES modes still being available, duplicate-looking TLS private-suite values, and no type safety around OR-composed fields. Test signals are descriptor hex dumps matching hardware manuals, crypto self-tests across block/hash/AEAD/PKC/protocol modes, hardware rejection indexes mapping to intended command words, and compile coverage for 32-bit and 64-bit pointer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h -->
