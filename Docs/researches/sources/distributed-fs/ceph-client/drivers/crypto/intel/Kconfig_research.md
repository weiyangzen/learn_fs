# sources/distributed-fs/ceph-client/drivers/crypto/intel/Kconfig Research

## Purpose
This Kconfig fragment is the Intel crypto driver menu aggregator. It includes the per-driver Kconfig files for Intel Keem Bay, IXP4xx, QAT, and IAA crypto support.

## Important APIs, Types, and Functions
There are no C APIs or runtime functions. The important entries are four `source` directives: `drivers/crypto/intel/keembay/Kconfig`, `drivers/crypto/intel/ixp4xx/Kconfig`, `drivers/crypto/intel/qat/Kconfig`, and `drivers/crypto/intel/iaa/Kconfig`.

## Control Flow
During Kconfig processing, this file pulls child menu/config definitions into the Intel crypto subtree. The IAA option researched in this subset is reachable only because this file sources `drivers/crypto/intel/iaa/Kconfig`.

## State and Persistence
It contributes build configuration symbols to the kernel `.config`. It has no runtime state.

## Dependencies and Integration Points
It integrates with the kernel Kconfig build system and the parent `drivers/crypto` Kconfig hierarchy. Its child entries control which Intel crypto driver directories the Makefile can build.

## Risks and Edge Cases
If a child Kconfig path is wrong or omitted, its driver options disappear from configuration even if source code exists. Ordering is simple and has no visible dependency logic here.

## Test Signals
Run `make menuconfig`/`olddefconfig` and verify Intel crypto options appear. Build coverage should confirm that enabling `CRYPTO_DEV_IAA_CRYPTO` reaches the IAA Makefile path.
