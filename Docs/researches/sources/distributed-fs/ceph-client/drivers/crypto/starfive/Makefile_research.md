# sources/distributed-fs/ceph-client/drivers/crypto/starfive/Makefile

## Purpose
This Makefile wires the StarFive JH7110 crypto driver objects into the kernel build. It builds one module or built-in object named `jh7110-crypto` when `CONFIG_CRYPTO_DEV_JH7110` is enabled.

## Important build behavior
`obj-$(CONFIG_CRYPTO_DEV_JH7110) += jh7110-crypto.o` declares the composite target. `jh7110-crypto-objs := jh7110-cryp.o jh7110-hash.o jh7110-rsa.o jh7110-aes.o` links the platform driver, hash implementation, RSA implementation, and AES implementation into that composite target.

## Integration points
The object list must stay aligned with prototypes in `jh7110-cryp.h`: `starfive_aes_register_algs()`, `starfive_hash_register_algs()`, and `starfive_rsa_register_algs()` are called from `jh7110-cryp.c`, so missing objects would break linking.

## Risks
Any new algorithm file needs to be added here and to the platform registration/unregistration sequence. Object ordering is relevant because the final module contains cross-object references, although normal kbuild resolves them within the composite object.

## Test signals
Build `CONFIG_CRYPTO_DEV_JH7110=m` and `=y`, confirm the resulting module name is `jh7110-crypto`, and check that all register/unregister symbols resolve.
