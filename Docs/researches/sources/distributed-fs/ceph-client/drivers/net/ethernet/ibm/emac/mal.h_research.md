
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.h

## Purpose
`mal.h` defines the Memory Access Layer register map, descriptor format, commac callback interface, per-MAL state, feature flags, and public MAL APIs used by EMAC core code.

## Important APIs, Types, and Functions
Register constants cover MAL CFG/ESR/IER, TX/RX channel active/reset/status registers, channel table pointers, and receive channel buffer size registers. `MAL_MAX_TX_SIZE` and `MAL_MAX_RX_SIZE` define the 4080-byte payload chunks; `mal_rx_size()` aligns RX sizes and `mal_tx_chunks()` estimates TX descriptor use. `struct mal_descriptor` is the hardware BD format. `struct mal_commac_ops` is the callback table for TX poll, RX poll, RX peek, and RX descriptor-error handling. `struct mal_commac` contains channel masks, flags, and list nodes. `struct mal_instance` stores hardware, NAPI, descriptor memory, registered commacs, and feature state. Public declarations expose channel management, polling, registration, and ethtool dump helpers.

## Control Flow
The header’s definitions are consumed by `mal.c` and `core.c`: EMAC fills `mal_commac`, MAL NAPI dispatches callbacks, and EMAC TX/RX code reads/writes descriptor control bits such as `MAL_RX_CTRL_EMPTY`, `MAL_RX_CTRL_FIRST`, `MAL_RX_CTRL_LAST`, `MAL_TX_CTRL_READY`, and `MAL_TX_CTRL_WRAP`.

## State and Persistence
All state is volatile kernel or device state. The descriptor format is shared with DMA hardware, so field sizes and endian behavior matter. `MAL_COMMAC_RX_STOPPED` and `MAL_COMMAC_POLL_DISABLED` are bit positions stored in `mal_commac.flags`.

## Dependencies and Integration Points
The file relies on DCR helpers via `dcr_read()`/`dcr_write()` wrappers and Kconfig feature symbols for special MAL behavior. Its API is the narrow integration point between the shared DMA engine and EMAC netdev instances.

## Risks
Descriptor-size constants and channel offsets must match allocation logic exactly. A bad `MAL_CHAN_MASK()` channel number can select the wrong hardware channel. Compile-time feature masks can silently disable support for a SoC whose device tree is present. The `mal_regs` dump reserves arrays for 32 channels, matching the implementation’s BUG_ON bounds.

## Test Signals
Build and runtime validation should cover descriptor wrap behavior, RX size alignment, TX chunk calculation for large packets, multi-channel channel-mask conflicts, and ethtool register dump size. Kconfig variants for `CONFIG_IBM_EMAC_MAL_CLR_ICINTSTAT` and `CONFIG_IBM_EMAC_MAL_COMMON_ERR` need compile coverage.
