# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.h

## Purpose
This header is the compile-time interface for optional IAA crypto statistics. It declares debugfs lifecycle and counter update functions when `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` is enabled, and otherwise replaces every function with an empty inline stub.

## Important APIs, Types, And Functions
- Enabled configuration declarations: `iaa_crypto_debugfs_init()`, `iaa_crypto_debugfs_cleanup()`, global update helpers, completion error update helpers, and workqueue update helpers.
- Disabled configuration stubs: exact-signature inline no-ops for all update functions and a zero-returning `iaa_crypto_debugfs_init()`.
- The workqueue APIs accept `struct idxd_wq *` but rely on other included driver headers to define it before use.

## Control Flow
Callers can unconditionally invoke stats hooks from IAA crypto code. The preprocessor either routes to the real implementation in `iaa_crypto_stats.c` or compiles away the calls with no runtime branch.

## State And Persistence
The header owns no state. It controls whether the state in `iaa_crypto_stats.c` exists at all.

## Dependencies And Integration Points
The file is consumed by IAA crypto code and coupled to the Kconfig symbol `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`. It also indirectly depends on IDXD workqueue types.

## Risks
- Disabled builds silently discard all stats, so tests that expect debugfs files must select the stats Kconfig option.
- The trailing `#endif // CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` uses C++ comment style, accepted by kernel C but less common than block comments in some older kernel code.

## Test Signals
- Build both with and without `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`.
- In disabled builds, verify callers link without `iaa_crypto_stats.c` and debugfs lifecycle calls return success/no-op.
