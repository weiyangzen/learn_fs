<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h

## Purpose
Declares the Falcon EF4 self-test result structures and exported self-test entry points consumed by ethtool-facing code and the RX loopback path.

## Important APIs, types, and functions
- `struct ef4_loopback_self_tests` stores per-TXQ sent/completed counts plus aggregate good/bad RX loopback counts.
- `struct ef4_self_tests` stores online test results, per-channel event queue results, offline memory/register results, PHY extended test results, and loopback results indexed by loopback mode.
- `EF4_MAX_PHY_TESTS` bounds PHY-specific results.
- Function declarations cover loopback RX packet inspection and synchronous/asynchronous self-test execution.

## Control flow
The header itself has no runtime control flow. It defines the data contract used by `selftest.c` and by consumers that display or interpret the test matrix.

## State and persistence behavior
The structures are caller-owned result containers. They do not persist beyond the caller's lifetime and do not own dynamic memory.

## Dependencies and integration points
Includes `net_driver.h` for EF4 constants such as `EF4_TXQ_TYPES`, `EF4_MAX_CHANNELS`, and loopback mode bounds. `ef4_loopback_rx_packet` is called from the receive path when `efx->loopback_selftest` is active.

## Risks and test signals
Risk is mainly ABI/contract drift between result arrays and the number of channels, TX queue types, loopback modes, or PHY tests. Test signals are successful compilation across all self-test consumers and correctly bounded ethtool output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.h -->
