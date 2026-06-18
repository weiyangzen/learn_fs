<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c

## Purpose
Provides EF4/Falcon online and offline self-tests for PHY liveness, NVRAM, interrupts, event queues, PHY-specific BIST, MAC/PHY loopback traffic, and asynchronous event interrupt diagnostics.

## Important APIs, types, and functions
- Public APIs: `ef4_selftest`, `ef4_loopback_rx_packet`, `ef4_selftest_async_start`, `ef4_selftest_async_cancel`, and `ef4_selftest_async_work`.
- Internal loopback model: `struct ef4_loopback_payload` and `struct ef4_loopback_state`.
- Online tests: `ef4_test_phy_alive`, `ef4_test_nvram`, `ef4_test_interrupts`, `ef4_test_eventq_irq`, and `ef4_test_phy`.
- Offline loopback flow: `ef4_test_loopbacks`, `ef4_wait_for_link`, `ef4_test_loopback`, `ef4_begin_loopback`, `ef4_poll_loopback`, and `ef4_end_loopback`.

## Control flow
`ef4_selftest` first cancels pending async diagnostics, runs online PHY/NVRAM/IRQ/eventq tests, and returns early on online failure. Without `ETH_TEST_FL_OFFLINE`, it runs PHY tests only. Offline tests detach the netdev, optionally run chip tests, force the PHY out of low power and loopback, run PHY tests, then test all supported loopback modes and enabled TX queue types. Loopback testing installs `efx->loopback_selftest`, reconfigures the port for each mode, waits for stable link, sends controlled UDP/IP payload bursts through specific TX queues, and validates returned packets in the RX path callback.

## State and persistence behavior
Self-test results are accumulated in `struct ef4_self_tests`, where non-counter tests use `1` for pass, `-1` for failure, and `0` for unavailable. Loopback uses transient heap state stored in `efx->loopback_selftest`, atomic RX good/bad counters, a payload iteration counter, and an SKB pointer array used to count TX completions. The original `phy_mode` and `loopback_mode` are restored before reattaching the device. No persistent storage is changed.

## Dependencies and integration points
Uses netdevice locking/detach, ethtool test flags, delayed work, jiffies timeouts, PCI/netif logging, and driver operations from `efx->type`, `efx->phy_op`, TX queue enqueue, RX loopback diversion, MAC lock protected reconfiguration, and NIC event/IRQ test hooks.

## Risks and test signals
Risks include false interrupt failures under high IRQ latency, disruptive offline tests affecting link traffic, loopback packet races during flush, and TX completion counting relying on SKB reference state. Strong test signals are per-channel event DMA/interrupt arrays, loopback `tx_sent`, `tx_done`, `rx_good`, `rx_bad`, PHY test names/results, timeout logs, and restoration of netdev attachment and original PHY state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/selftest.c -->
