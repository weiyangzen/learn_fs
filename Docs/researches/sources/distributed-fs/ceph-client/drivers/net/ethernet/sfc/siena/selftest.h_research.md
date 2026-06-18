<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h

## Purpose
Declares the Siena self-test result structures and public self-test entry points used by ethtool, RX loopback handling, and asynchronous interrupt diagnostics.

## Important APIs, Types, And Functions
- `struct efx_loopback_self_tests` records per-TXQ sent/completed counts and aggregate RX good/bad counts.
- `struct efx_self_tests` contains online test results, offline chip/PHY results, and loopback results indexed by `LOOPBACK_TEST_MAX`.
- `EFX_MAX_PHY_TESTS` bounds PHY vendor-specific test results.
- Declared APIs are `efx_siena_loopback_rx_packet()`, `efx_siena_selftest()`, `efx_siena_selftest_async_init()`, `efx_siena_selftest_async_start()`, and `efx_siena_selftest_async_cancel()`.

## Control Flow
The header exposes a simple control surface: ethtool invokes `efx_siena_selftest()`, RX code calls `efx_siena_loopback_rx_packet()` when loopback self-test state is installed, and probe/open paths initialize/start/cancel delayed async interrupt checks.

## State And Persistence Behavior
The file only declares in-memory result containers. The result convention is documented: non-counter tests use `1` for success, `-1` for failure, and `0` when not run or unsupported. No persistent state or storage format is introduced.

## Dependencies And Integration Points
Includes `net_driver.h` for `struct efx_nic`, channel/TX queue constants, and loopback mode definitions. It integrates with `ethtool_common.c`, Siena RX paths, and common driver lifecycle code that owns `efx->selftest_work`.

## Risks And Test Signals
Array dimensions must stay aligned with driver constants such as `EFX_MAX_CHANNELS`, `EFX_MAX_TXQ_PER_CHANNEL`, and `LOOPBACK_TEST_MAX`. Useful test signals are compile-time coverage of structure consumers and ethtool self-test output matching these result fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.h -->
