# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.c

## Purpose
Implements ath12k Copy Engine host-side transport rings. CE pipes are the low-level DMA path used by HTC/WMI/firmware messaging and some data paths to move sk_buffs between host and target firmware through HAL SRNG descriptors.

## Important APIs, Types, And Functions
Exports `ath12k_ce_alloc_pipes()`, `ath12k_ce_init_pipes()`, `ath12k_ce_free_pipes()`, `ath12k_ce_cleanup_pipes()`, `ath12k_ce_send()`, `ath12k_ce_per_engine_service()`, `ath12k_ce_rx_post_buf()`, `ath12k_ce_poll_send_completed()`, `ath12k_ce_get_shadow_config()`, and `ath12k_ce_get_attr_flags()`. The internal helpers allocate coherent descriptor rings, post RX buffers, reap destination status entries, reap source completions, and configure MSI/shadow-register parameters.

## Control Flow
Probe allocates pipe rings from `hw_params->host_ce_config`, then firmware-ready flow initializes SRNG rings and posts RX buffers. TX maps an skb before `ath12k_ce_send()`, which writes a HAL CE source descriptor and records the skb by ring index. Interrupt or polling service calls `ath12k_ce_per_engine_service()`, which reaps TX completions and invokes receive callbacks after unmapping and length-validating RX buffers. RX buffers are replenished immediately; allocation failures arm `rx_replenish_retry`.

## State And Persistence
State is in `ab->ce.ce_pipe[]`: source, destination, status rings, cached `write_index`/`sw_index`, skb owner arrays, `rx_buf_needed`, callbacks, and `ce_lock`. DMA-coherent descriptor memory persists for device lifetime. Posted RX skbs persist until firmware fills them or cleanup unmaps them. Shadow CE register config is cached in `ab->qmi.ce_cfg`.

## Dependencies And Integration Points
Depends on HAL SRNG/CE descriptor helpers, HIF MSI helpers, hw params, DMA APIs, timers, sk_buffs, and debug logging. It integrates with QMI startup via shadow config, HTC/WMI through CE pipes, and crash recovery through cleanup and crash-flush checks.

## Risks
Ring accounting must stay synchronized with HAL SRNG ownership; mismatched indices can leak skbs or corrupt DMA ownership. `ath12k_ce_cleanup_pipes()` only polls disabled-interrupt TX rings and has a note questioning full TX cleanup. RX replenish failures can degrade firmware messaging until retry succeeds. Lock ordering between `ce_lock` and SRNG locks is part of the correctness contract.

## Test Signals
Boot should show CE allocation/init success and WMI/HTC readiness. Stress WMI traffic, firmware restart, and low-memory RX replenish paths. Exercise interrupt-disabled pipes to verify polling completions. DMA debug, lockdep, and KASAN are useful for mapping lifetime and lock-order regressions.
