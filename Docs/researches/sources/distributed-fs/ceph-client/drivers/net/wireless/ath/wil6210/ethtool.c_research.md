# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/ethtool.c

## Purpose
`ethtool.c` provides the wil6210 ethtool hooks, currently focused on interrupt coalescing. It lets users inspect and configure RX/TX interrupt moderation thresholds while reusing cfg80211's standard driver-info implementation.

## Important APIs, Types, And Functions
`wil_ethtoolops_get_coalesce()` reads TX and RX interrupt timer control/threshold registers and reports `tx_coalesce_usecs` and `rx_coalesce_usecs`. `wil_ethtoolops_set_coalesce()` validates requested usec thresholds, rejects monitor mode, stores values in `wil->tx_max_burst_duration` and `wil->rx_max_burst_duration`, resumes the device through runtime PM, and invokes `wil->txrx_ops.configure_interrupt_moderation()`. `wil_set_ethtoolops()` installs the static `wil_ethtool_ops` table on a netdev.

## Control Flow
Both get and set operations serialize on `wil->mutex`. Get resumes the PCI device, reads legacy interrupt moderation registers (`RGF_DMA_ITR_TX_CNT_CTL`, `RGF_DMA_ITR_TX_CNT_TRSH`, `RGF_DMA_ITR_RX_CNT_CTL`, `RGF_DMA_ITR_RX_CNT_TRSH`), then autosuspends. Set rejects unsupported monitor-mode coalescing because monitor mode prefers timestamp precision, bounds values by `WIL6210_ITR_TRSH_MAX`, updates cached driver configuration, and asks the active TX/RX backend to reprogram moderation.

## State And Persistence
The configured values are stored in `wil6210_priv` and survive until driver reset/reconfiguration or module unload. The actual hardware state is rewritten through the TX/RX ops path when set, and also during firmware bring-up from `main.c`.

## Dependencies And Integration Points
This file depends on netdev ethtool APIs, cfg80211 driver info, runtime PM wrappers from `pm.c`, register helpers from `wil6210.h`, and interrupt moderation implementations in `interrupt.c`. `netdev.c` calls `wil_set_ethtoolops()` for every allocated VIF netdev.

## Risks
Only usec coalescing fields are honored; other ethtool coalescing fields are ignored and invalid values return `-EINVAL`. Register reads are legacy register specific, while set delegates through `txrx_ops`; EDMA behavior should be verified to ensure reported values remain meaningful. Runtime PM failures propagate directly.

## Test Signals
Exercise `ethtool -c` and `ethtool -C` while the device is active, suspended, in monitor mode, and using EDMA/legacy DMA. Check threshold boundary values above `WIL6210_ITR_TRSH_MAX`, runtime PM failure injection, and whether interrupts are reprogrammed after reset.
