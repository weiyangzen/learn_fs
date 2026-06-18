
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.c

## Purpose
`mal.c` implements the IBM EMAC Memory Access Layer, a shared DMA engine that owns descriptor memory, DCR register programming, interrupt handling, and NAPI dispatch for one or more communication MACs (`mal_commac`) such as EMAC instances.

## Important APIs, Types, and Functions
Public functions include `mal_register_commac()`, `mal_unregister_commac()`, `mal_set_rcbs()`, `mal_tx_bd_offset()`, `mal_rx_bd_offset()`, channel enable/disable routines, `mal_poll_add()`, `mal_poll_del()`, `mal_poll_disable()`, `mal_poll_enable()`, `mal_get_regs_len()`, `mal_dump_regs()`, `mal_init()`, and `mal_exit()`. Internal IRQ handlers are `mal_serr()`, `mal_txeob()`, `mal_rxeob()`, `mal_txde()`, `mal_rxde()`, and `mal_int()` for common-error configurations. `mal_poll()` is the shared NAPI poller.

## Control Flow
Probe allocates `struct mal_instance`, reads OF `num-tx-chans`/`num-rx-chans`, maps DCRs, sets feature flags for special SoCs, initializes lists/lock/NAPI, resets MAL, configures MAL CFG, allocates coherent descriptor memory for all TX/RX channels, writes channel table pointer DCRs, requests interrupts, enables MAL error events and EOB interrupts, then publishes drvdata. EMAC probe registers a `mal_commac`, which claims TX/RX channel masks and enables NAPI if it is the first user. End-of-buffer IRQs schedule NAPI and disable EOB interrupts; NAPI calls each registered commac’s TX reclaim then RX poll callbacks, completes, reenables EOB interrupts, and checks for rotting packets or stopped RX channels. Descriptor-error IRQs set `MAL_COMMAC_RX_STOPPED` and call the commac `rxde` callback for affected RX channels.

## State and Persistence
`struct mal_instance` holds DCR host mapping, channel counts, IRQ numbers, commac lists, NAPI object, channel allocation masks, coherent descriptor memory, feature flags, and a dummy netdev used for NAPI. State is volatile. Descriptor memory is coherent DMA and shared with EMAC users by offset.

## Dependencies and Integration Points
The module depends on platform/OF probing, PowerPC DCR access, DMA coherent allocation, NAPI, IRQs, local `core.h`/`mal.h`, and EMAC commac callbacks. Device-tree compatible strings distinguish MAL v1/v2, Axon behavior, and legacy type matches. EMAC uses MAL offsets and channel APIs to operate its rings.

## Risks
MAL is shared: channel-mask conflicts or list misuse can break multiple EMACs. NAPI fairness is explicitly simple and may favor earlier poll-list entries. RX channel numbering has a special divide-by-eight adjustment for certain SoCs, which is easy to regress. IRQ error handling often logs and continues; PLB/OPB errors may indicate bad DMA addresses or hardware setup. Removal warns if commacs remain registered.

## Test Signals
Probe logs showing MAL version and channel counts, successful EMAC registration with non-conflicting channels, TX/RX EOB interrupt activity, NAPI traffic on multiple EMACs, descriptor-error recovery, `ethtool -d` MAL register dump content, and removal without non-empty commac-list warnings are key signals. SoC variants with common error interrupt and clear-ICINTSTAT behavior need targeted coverage.
