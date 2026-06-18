# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/tx.h

## Purpose
Defines WiLink 8 TX constants and the immediate TX completion prototype.

## Important APIs, types, and functions
- `WL18XX_TX_HW_BLOCK_SPARE`, `WL18XX_TX_HW_EXTRA_BLOCK_SPARE`, and `WL18XX_TX_HW_BLOCK_SIZE` shape TX memory-block accounting.
- TX status macros split descriptor id and success/failure bit from firmware status bytes.
- `WL18XX_TX_CTRL_NOT_PADDED` marks frames not padded to SDIO block size.
- `CONF_TX_RATE_USE_WIDE_CHAN` is a firmware rate-policy flag for wide channels.
- `wl18xx_tx_immediate_complete()` is exported to wl18xx ops.

## Control flow
No executable flow. Constants are consumed by `tx.c` and `main.c` TX descriptor setup.

## State and persistence behavior
No local state. Constants influence firmware TX descriptor and rate-policy state.

## Dependencies and integration points
Includes wlcore core definitions. Integrated by wl18xx TX completion and descriptor helpers.

## Risks and test signals
Wrong block size/spare counts can cause firmware memory accounting failures; wrong status masks corrupt TX completion. Test with normal traffic, TKIP/GEM extra spare blocks, SDIO padding, and HT40 rate policies.
