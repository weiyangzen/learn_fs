# sources/distributed-fs/ceph-client/include/soc/fsl/dcp.h

Purpose: defines protected-AES key slot handles for NXP MXS DCP crypto users.

Important APIs and types: `DCP_PAES_KEYSIZE` marks the one-byte protected-key handle size. Slot constants identify hardware key slots 0-3, the device-unique key, and OTP key handles for `crypto_skcipher_setkey()` style use.

Control flow: crypto clients select a protected key by passing one of these handles as the key material to DCP-backed AES operations.

State and persistence: key material itself resides in DCP hardware/OTP/unique key sources. The header only defines selector values and stores no state.

Dependencies and integration points: standalone header integrated with the MXS DCP crypto driver and protected-key consumers.

Risks and test signals: risks include treating one-byte handles as raw AES keys, accepting invalid slot values, and mismatched userspace/key-management expectations. Test PAES setkey with each supported slot, invalid handle rejection, OTP/unique key behavior, and disabled/non-DCP build coverage.
