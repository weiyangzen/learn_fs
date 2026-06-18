# sources/distributed-fs/ceph-client/drivers/crypto/marvell/Kconfig

Purpose: declares Marvell crypto driver configuration symbols for CESA, OcteonTX CPT, and OcteonTX2 CPT.

Important declarations: `CRYPTO_DEV_MARVELL` is a shared tristate selected by concrete drivers. `CRYPTO_DEV_MARVELL_CESA` depends on Orion/MVEBU platforms or compile testing and selects AES/DES libraries, skcipher, hash, SRAM, and the Marvell umbrella symbol. OcteonTX and OcteonTX2 CPT options depend on appropriate architectures, PCI MSI, 64-bit, and select crypto/hash/AEAD/authenc support plus Marvell umbrella; OcteonTX2 also selects mailbox/devlink-related networking support.

Control flow and integration: these symbols drive the Marvell Makefile subdirectories. CESA builds the platform crypto engine researched in this subset; CPT symbols build separate PCI accelerator families.

State and persistence: build configuration only.

Risks and test signals: dependency/select drift can produce build failures when compile-testing. CESA needs SRAM and crypto library selects for the code paths in `cesa/`. Build matrix should cover platform, module, and `COMPILE_TEST` cases.
