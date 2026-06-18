# sources/distributed-fs/ceph-client/crypto/Makefile

Purpose: maps crypto Kconfig symbols to built objects and composite modules for the Linux crypto subsystem. It is the build-time contract connecting selected algorithms, templates, API front ends, userspace interfaces, and architecture-sensitive AEGIS NEON objects.

Important APIs, types, and functions: this is kbuild metadata. It defines composite objects such as `crypto.o`, `crypto_algapi.o`, `crypto_skcipher.o`, `crypto_hash.o`, `crypto_acompress.o`, `cryptomgr.o`, `rsa_generic.o`, `ecdsa_generic.o`, `ecdh_generic.o`, `ecrdsa_generic.o`, `jitterentropy_rng.o`, `crc32c-cryptoapi.o`, `crc32-cryptoapi.o`, and `aegis128-y`.

Control flow and behavior: `obj-$(CONFIG_...)` lines include modules or built-ins according to Kconfig. Core front ends build from multiple source files, e.g. `crypto_hash-y := ahash.o shash.o`, `crypto_algapi-y := algapi.o scatterwalk.o proc.o`, and `cryptomgr-y := algboss.o testmgr.o`. Architecture conditionals add AEGIS NEON glue only for ARM/ARM64 when `CONFIG_CRYPTO_AEGIS128_SIMD` is enabled and attach special compiler flags.

State and persistence: the file has no runtime state; it determines build artifacts, module composition, generated ASN.1 dependencies, and compile flags. Its decisions persist in the built kernel tree as object membership and module names.

Dependencies and integration points: it depends directly on Kconfig symbols from `crypto/Kconfig`, generated ASN.1 files, compiler capability macros, and architecture settings. Runtime integration follows from objects included here: AF_ALG modules, algorithm modules, crypto manager, FIPS support, async_tx, asymmetric keys, and Kerberos crypto.

Risks and correctness concerns: mismatched Kconfig and Makefile entries cause selected algorithms to be unavailable or unselected files to build. Composite object omissions are easy to miss for template modules and generated ASN.1 helpers. ARM64 AEGIS flags are sensitive: NEON/AES intrinsics need `-ffreestanding`, crypto CPU features, GCC fixed vector registers, and removal of `-mgeneral-regs-only`.

Test signals: compare every selected Kconfig symbol against an object rule, run representative `make M=crypto` and full kernel builds for ARM, ARM64, x86, and allmodconfig. Verify module aliases load expected objects such as `af_alg`, `algif_hash`, `aegis128`, `adiantum`, and `aes`; test generated ASN.1 dependency rebuilds.
