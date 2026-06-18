<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h

Purpose: centralizes QCE algorithm flags, size constants, template structure, and shared helper prototypes.

Important definitions: constants cover sector size, HMAC/cipher key sizes, IV/nonce sizes, burst alignment, algorithm bits for DES/3DES/AES/SHA/HMAC/CMAC, mode bits for CBC/ECB/CTR/XTS/CCM/RFC4309, and direction bits. Predicate macros such as `IS_AES()`, `IS_SHA_HMAC()`, `IS_CCM()`, and `IS_ENCRYPT()` are used throughout setup and algorithm files. `struct qce_alg_template` wraps one registered crypto algorithm with flags, device pointer, optional standard IV, zero-hash pointer, and list entry.

Control flow and integration: algorithm files allocate templates, set flags, and register the union member matching their crypto type. Core dispatch and common register setup use the template to find the QCE device and mode flags.

State and persistence: templates persist for registered algorithm lifetimes and are linked in per-family lists. The header itself has no runtime state.

Dependencies: Linux crypto API headers, AES/hash/skcipher/AEAD internals, and QCE core declarations.

Risks and test signals: flag bit overlap would misprogram hardware, so all feature combinations should be build- and runtime-tested. Template union use requires callers to recover the correct container for each crypto type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h -->
