## sources/distributed-fs/ceph-client/drivers/crypto/nx/Makefile

Purpose: maps the NX Kconfig symbols to kernel objects and groups the encryption, compression core, and platform-specific compression modules.

Important build objects: `nx-crypto.o` includes `nx.o`, AES ECB/CBC/GCM/CCM/CTR/XCBC wrappers, SHA256, and SHA512. `nx_debugfs.o` is conditionally appended under `CONFIG_DEBUG_FS`. `nx-compress.o` contains the shared `nx-842.o` crypto API shim. `nx-compress-pseries.o` and `nx-compress-powernv.o` each contain their platform backend.

Control flow and integration: the object grouping establishes link-time visibility among wrapper files. The AES/SHA wrapper files export algorithm descriptors consumed by `nx.o`, and `nx.o` supplies shared context allocation, scatterlist construction, OF capability parsing, and registration. For compression, platform modules depend on exported symbols from `nx-842.c` for context allocation and crypto API compress/decompress entry points.

State and persistence: build-only metadata; no runtime state.

Dependencies: depends on Kbuild, `CONFIG_CRYPTO_DEV_NX_ENCRYPT`, `CONFIG_CRYPTO_DEV_NX_COMPRESS_PSERIES`, `CONFIG_CRYPTO_DEV_NX_COMPRESS_POWERNV`, and `CONFIG_DEBUG_FS`.

Risks: because platform compression modules and shared compression core are linked as separate objects, symbol exports from `nx-842.c` must remain aligned with platform users. Adding a new AES/SHA wrapper requires updating both this Makefile and `nx.h`/`nx.o` registration tables. Debugfs inclusion must not make core registration depend on debugfs symbols when disabled.

Test signals: compile tests should verify all Kconfig combinations, especially debugfs on/off and platform modules as loadable modules. Link checks should catch missing exported algorithm descriptors or compression symbols.
