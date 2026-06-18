# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/Kconfig Research

## Purpose
This Kconfig file defines configuration switches for the Intel Analytics Accelerator (IAA) compression accelerator crypto driver and its optional statistics support.

## Important APIs, Types, and Functions
`CONFIG_CRYPTO_DEV_IAA_CRYPTO` is a tristate option titled `Support for Intel(R) IAA Compression Accelerator`. It depends on `CRYPTO_DEFLATE` and `INTEL_IDXD`, defaults to `n`, and builds module `iaa_crypto` when selected as a module. `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` is a bool option depending on IAA crypto and enables per-device, per-workqueue, and global driver statistics.

## Control Flow
Configuration selection controls whether the IAA directory is entered by the Intel Makefile and whether `iaa_crypto_stats.o` is added by the IAA Makefile. Runtime code in `iaa_crypto_main.c` also compiles against stats update functions that are either real functions or inline no-ops depending on the stats symbol.

## State and Persistence
The selected symbols persist in kernel `.config` and govern built-in/module output. They have no direct runtime storage, although enabling stats adds runtime counters and debugfs files in companion code.

## Dependencies and Integration Points
The driver requires the Intel IDXD bus/workqueue infrastructure and the Crypto API deflate implementation. The dependency on `CRYPTO_DEFLATE` is important because the IAA driver registers an acomp `deflate` implementation and uses generic deflate fallback for some decompression errors.

## Risks and Edge Cases
Missing `INTEL_IDXD` prevents the driver from binding to IAA workqueues. Missing `CRYPTO_DEFLATE` would break fallback and algorithm integration, so it is correctly enforced. Stats are optional, so code paths must remain valid with no-op stats functions.

## Test Signals
Kconfig tests should verify dependency enforcement, module name `iaa_crypto`, stats object inclusion only when requested, and successful builds for built-in and module configurations.
