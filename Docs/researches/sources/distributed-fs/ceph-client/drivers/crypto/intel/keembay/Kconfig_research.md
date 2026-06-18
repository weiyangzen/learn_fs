# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Kconfig

## Purpose
This Kconfig file defines build options for Intel Keem Bay OCS crypto accelerators: AES/SM4, optional ECB and CTS modes, ECC/ECDH, HCU hash/HMAC, and optional SHA224/HMAC-SHA224.

## Important APIs, Types, And Functions
- `CRYPTO_DEV_KEEMBAY_OCS_AES_SM4`: tristate AES/SM4 accelerator selecting SKCIPHER, AEAD, and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_AES_SM4_ECB` and `_CTS`: optional bools gated by the AES/SM4 driver, with help text warning Intel does not recommend those modes.
- `CRYPTO_DEV_KEEMBAY_OCS_ECC`: tristate ECDH accelerator requiring OF and I/O memory and selecting ECDH and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_HCU`: tristate hash/HMAC accelerator selecting HASH and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_HCU_HMAC_SHA224`: optional SHA224/HMAC-SHA224 support, disabled by default because Intel recommends not using those algorithms.

## Control Flow
Kconfig symbols control which platform drivers and algorithms are compiled. The AES/SM4 optional symbols conditionally include ECB/CTS algorithm registrations and module aliases in `keembay-ocs-aes-core.c`; the HCU SHA224 symbol conditionally includes SHA224 algorithm table entries.

## State And Persistence
No runtime state is stored here. The file determines compile-time driver coverage.

## Dependencies And Integration Points
The symbols integrate with `keembay/Makefile` and the Linux Crypto API. Platform drivers require Keem Bay hardware or `COMPILE_TEST`; ECC and HCU also require Open Firmware device matching.

## Risks
- Optional unsafe/legacy modes are deliberately exposed when selected; downstream configs must choose them intentionally.
- Compile-test builds cannot validate register-level behavior.

## Test Signals
- Build matrix covering base AES/SM4, optional ECB/CTS, ECC, HCU, and SHA224.
- Confirm optional algorithm aliases appear only when the related Kconfig symbols are enabled.
