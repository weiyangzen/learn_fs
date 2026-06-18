# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/selftest.c

## Purpose
Implements ethtool self-test execution for the top-level SFC driver variant: PHY liveness, NVRAM, interrupt delivery, event queue DMA/interrupt tests, optional chip memory/register tests, PHY extended tests, loopback tests, and asynchronous event-queue interrupt smoke testing after open.

## Important APIs, types, and functions
`struct efx_loopback_payload` defines the synthetic Ethernet/IP/UDP loopback frame, while `struct efx_loopback_state` is temporary state hung from `efx->loopback_selftest`. `efx_selftest()` is the main ethtool entry point. `efx_loopback_rx_packet()` validates received loopback packets. Async helpers initialize, start, and cancel delayed event interrupt checks.

Important helpers include `efx_test_interrupts()`, `efx_test_eventq_irq()`, `efx_test_phy()`, `efx_begin_loopback()`, `efx_end_loopback()`, `efx_test_loopback()`, `efx_test_loopbacks()`, and `efx_wait_for_link()`.

## Control flow
Online tests run first and return immediately on hard failure: PHY alive, optional NVRAM, direct interrupt generation, and per-channel event queue testing. Offline tests detach the netdev, run chip tests if available, power/configure the PHY, iterate supported loopback modes, send increasing packet bursts through enabled TX queue types, wait for RX callbacks, count TX completions, then restore original PHY and loopback state and reattach.

## State and persistence behavior
The file mutates in-memory NIC state only: `phy_mode`, `loopback_mode`, `loopback_selftest`, delayed work, and `struct efx_self_tests` results. `state->flush` prevents in-flight packets from being counted during transitions. There is no on-disk persistence.

## Dependencies and integration points
Depends on MCDI PHY helpers, NIC type callbacks (`test_nvram`, `test_chip`), channel/event/IRQ abstractions, TX enqueue, RX loopback callback integration, reset scheduling, and netdev detach/attach helpers.

## Risks
The sensitive areas are RX callback lifetime, memory ordering between sender and RX path, event queue stop/start during inspection, and offline disruption. Timeouts can produce false negatives on heavily delayed interrupt systems. Failed restore paths can leave PHY/loopback state wrong if not carefully preserved.

## Test signals
Use ethtool online/offline self-tests across MSI-X/MSI/legacy, multi-channel RSS, checksum-offload queues, and loopback modes. Expected loopback signal is `tx_sent == tx_done == rx_good` and `rx_bad == 0`.
