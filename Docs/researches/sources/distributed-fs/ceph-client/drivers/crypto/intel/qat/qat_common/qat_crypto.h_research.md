# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.h

Purpose: defines QAT crypto instance and per-request state shared by QAT symmetric, AEAD, and asymmetric send paths.

Important APIs and types: `struct qat_crypto_instance` stores symmetric TX/RX rings, PKE TX/RX rings, owner accelerator, list linkage, ID, refcount, and backlog. `struct qat_crypto_request` embeds the firmware LA bulk request, points to AEAD or skcipher context/request, owns mapped buffer metadata, callback pointer, IV storage, encryption flag, and low-level algorithm request state. `adf_hw_dev_has_crypto()` checks symmetric, asymmetric, and authentication capability bits.

Control flow and integration: algorithm implementations allocate/fill `qat_crypto_request`, submit it on a selected `qat_crypto_instance`, and receive completion through the callback stored in the request. The IV union supports both structured 128-bit big-endian access and byte-array AES block access. The instance struct is populated by `qat_crypto.c`.

State and persistence: instance state lasts for the accelerator service lifetime; request state is per crypto operation and should be zeroed or freed by callers after callback completion. The backlog is shared across send paths and requires its lock.

Dependencies: depends on Linux crypto AES constants, QAT firmware LA structures, buffer-list support, and QAT algorithm send helpers. The capability helper assumes inverted `accel_capabilities_mask` semantics.

Risks and test signals: request unions require callers to keep the context/request type consistent with the algorithm path. Capability checks require all three crypto/auth bits, so devices with only symmetric crypto are rejected by this helper. Tests should cover IV preservation, request callback dispatch, buffer mapping cleanup, and capability mask combinations.
