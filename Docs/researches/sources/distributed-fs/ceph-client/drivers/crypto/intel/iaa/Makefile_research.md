# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Makefile Research

## Purpose
This Makefile builds the Intel IAA crypto module and sets include paths and symbol namespace defaults required for IDXD integration.

## Important APIs, Types, and Functions
`ccflags-y` adds the IDXD driver include path and defines `DEFAULT_SYMBOL_NAMESPACE` as `"IDXD"`. `obj-$(CONFIG_CRYPTO_DEV_IAA_CRYPTO) := iaa_crypto.o` creates the module or built-in object. `iaa_crypto-y` is composed from `iaa_crypto_main.o` and `iaa_crypto_comp_fixed.o`. `iaa_crypto-$(CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS)` conditionally adds `iaa_crypto_stats.o`.

## Control Flow
Kbuild evaluates this file only when the parent Intel Makefile descends into `iaa/`. The composite object is linked from the listed translation units. Stats functions resolve either to compiled stats code or inline no-ops from the stats header depending on configuration.

## State and Persistence
The Makefile affects build artifacts and symbol namespace metadata. It has no runtime state.

## Dependencies and Integration Points
It integrates with `drivers/dma/idxd` headers and the IDXD exported symbol namespace. It connects Kconfig symbols to actual objects.

## Risks and Edge Cases
The namespace define and `MODULE_IMPORT_NS("IDXD")` in the C file must remain aligned with IDXD exports. Missing `iaa_crypto_comp_fixed.o` would leave the fixed Huffman mode unregistered. Missing stats object when stats are enabled would break debugfs/stat update linkage.

## Test Signals
Build with IAA enabled/disabled and stats enabled/disabled. Inspect `modinfo iaa_crypto` and link output for expected objects and IDXD namespace imports.
