# sources/distributed-fs/ceph-client/arch/powerpc/crypto/Makefile

Purpose: builds PowerPC crypto accelerated objects and generated assembly based on enabled Kconfig options.

Important APIs/types/functions: build variables/targets `obj-$(CONFIG_CRYPTO_AES_PPC_SPE)`, `obj-$(CONFIG_CRYPTO_AES_GCM_P10)`, `obj-$(CONFIG_CRYPTO_DEV_VMX_ENCRYPT)`, `aes-ppc-spe-y`, `aes-gcm-p10-crypto-y`, `vmx-crypto-objs`, `quiet_cmd_perl`, `targets`, `OBJECT_FILES_NON_STANDARD_aesp10-ppc.o`, `OBJECT_FILES_NON_STANDARD_ghashp10-ppc.o`. Source size is 35 lines / 933 bytes.

Control flow is Kconfig/Makefile selection: CPU feature symbols choose which objects are compiled, Perl generators emit assembly, and module registration code later exposes the algorithms to the crypto API.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include wrong CPU feature dependencies, missing generated objects, module alias conflicts, or stale assembly generator output. Test signals are all relevant PowerPC crypto Kconfig build combinations and crypto selftest availability at boot/module load.
