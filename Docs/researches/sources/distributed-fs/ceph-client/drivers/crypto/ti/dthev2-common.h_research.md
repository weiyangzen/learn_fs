
# sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.h

Purpose: shared definitions for the TI DTHE V2 driver. It defines device, transform, request, mode, timeout, and helper prototypes used by the common platform layer and AES implementation.

Important APIs, types, and functions: constants include `DTHE_REG_SIZE`, `DTHE_DMA_TIMEOUT_MS`, and `DTHE_MAX_KEYSIZE`. `enum dthe_aes_mode` enumerates ECB/CBC/CTR/XTS/GCM/CCM. `struct dthe_data` stores device, MMIO base, list node, crypto engine, and AES/SHA DMA channels. `struct dthe_tfm_ctx` holds per-transform key/auth/mode state and a union of skcipher or AEAD fallback transforms. `struct dthe_aes_req_ctx` carries request direction, padding, and completion. Prototypes cover device lookup, scatterlist copy, and AES algorithm registration.

Control flow: the header itself has no runtime control flow, but it fixes the contracts used by `dthev2-common.c` probe/device management and `dthev2-aes.c` request execution. The fallback pointer union relies on each algorithm family using the correct init/exit path.

State and persistence: all defined state is in-memory kernel driver state. The largest secret-bearing allocation is `dthe_tfm_ctx.key`, sized for XTS-AES-256. Request padding is transient and should be zeroed by users after partial-block handling.

Dependencies and integration points: includes Linux crypto internal headers, DMA engine, DMA mapping, scatterlist, I/O helpers, and AES/hash types. It is the private ABI between DTHE source files, not an external userspace ABI.

Risks and test signals: the union between AEAD and skcipher fallback pointers saves space but makes algorithm init/exit pairing important. `DTHE_DMA_TIMEOUT_MS` controls request completion behavior globally. Tests should verify transform context size, request context size, and that every algorithm using fallback initializes and frees the correct union member.
