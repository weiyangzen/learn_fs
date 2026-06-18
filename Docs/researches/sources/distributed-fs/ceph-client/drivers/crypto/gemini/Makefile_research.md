# sources/distributed-fs/ceph-client/drivers/crypto/gemini/Makefile

Purpose: declares the object composition for the Gemini/Storlink SL3516 crypto engine driver.

Important APIs and control flow: when `CONFIG_CRYPTO_DEV_SL3516` is enabled, the build creates the `sl3516-ce.o` module or built-in object. The composite object is formed from `sl3516-ce-core.o`, `sl3516-ce-cipher.o`, and `sl3516-ce-rng.o`, which respectively provide platform/device registration, skcipher offload, and hwrng registration.

State and persistence behavior: the Makefile has no runtime state. Its persistent effect is link-time inclusion of all three driver components under one Kconfig symbol, so cipher and RNG support are not independently selectable.

Dependencies and integration points: depends on the parent crypto driver Kconfig selecting `CONFIG_CRYPTO_DEV_SL3516`. The object list assumes all shared declarations live in `sl3516-ce.h` and that core code calls the cipher and RNG helper entry points.

Risks and test signals: risks include unresolved symbols if any component is omitted, inability to build only RNG or only cipher support, and Kconfig dependency mistakes surfacing only at link or modpost time. Test signals are successful `CONFIG_CRYPTO_DEV_SL3516=m` and built-in builds, module containing platform driver plus hwrng and skcipher symbols, and no stale object names after file renames.
