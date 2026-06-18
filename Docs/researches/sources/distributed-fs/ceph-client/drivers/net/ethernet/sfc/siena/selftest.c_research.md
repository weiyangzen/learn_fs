<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c

## Purpose
Implements Siena online/offline ethtool self-tests: PHY liveness, NVRAM, IRQ generation, event queue interrupt/DMA delivery, PHY extended tests, chip register tests through the NIC type, and disruptive MAC/PHY loopback traffic.

## Important APIs, Types, And Functions
- Public entry points: `efx_siena_selftest()`, `efx_siena_loopback_rx_packet()`, `efx_siena_selftest_async_init()`, `efx_siena_selftest_async_start()`, and `efx_siena_selftest_async_cancel()`.
- Test result ABI: `struct efx_self_tests` and per-loopback counters in `struct efx_loopback_self_tests`.
- Loopback internals: packed `struct efx_loopback_payload`, transient `struct efx_loopback_state`, `efx_begin_loopback()`, `efx_end_loopback()`, `efx_test_loopback()`, and `efx_test_loopbacks()`.
- Online diagnostics: `efx_test_phy_alive()`, `efx_test_nvram()`, `efx_test_interrupts()`, `efx_test_eventq_irq()`, and `efx_test_phy()`.

## Control Flow
`efx_siena_selftest()` cancels pending async IRQ diagnostics, runs non-disruptive PHY/NVRAM/interrupt/eventq checks, and aborts on online failure. Without `ETH_TEST_FL_OFFLINE`, it finishes with PHY tests. Offline mode detaches the netdev, runs the NIC type chip test if available, forces PHY out of low power and loopback, runs PHY tests, then iterates all supported loopback modes and enabled TX queue types. Each loopback mode reconfigures the port under `mac_lock`, waits for two stable link-up samples, sends increasing packet bursts through a chosen TX queue, and validates returned packets in the RX callback.

## State And Persistence Behavior
State is runtime-only. Results are written into the caller-supplied `struct efx_self_tests`, using `1` pass, `-1` failure, and `0` unavailable. Loopback state is temporarily installed at `efx->loopback_selftest`; received packets are either dropped during flush or validated and counted with atomics. The original PHY mode and loopback mode are restored before reattaching the netdev.

## Dependencies And Integration Points
Depends on Siena MCDI PHY/NVRAM tests, farch event/IRQ test hooks, TX enqueue, RX loopback diversion, netdevice detach/attach, delayed work, ethtool flags, `mac_lock`, and the NIC type callback table (`test_chip`, `test_nvram`, `monitor`, `check_mac_fault`).

## Risks And Test Signals
Long IRQ latency can cause false interrupt failures despite the one-second timeout. Offline tests are disruptive and must restore device state after errors. Loopback validation is sensitive to stale in-flight packets, so `flush` and memory barriers are important. Test signals are per-channel eventq DMA/interrupt arrays, loopback `tx_sent`, `tx_done`, `rx_good`, `rx_bad`, PHY extended results, timeout logs, and reset scheduling after unrecoverable chip-test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/selftest.c -->
