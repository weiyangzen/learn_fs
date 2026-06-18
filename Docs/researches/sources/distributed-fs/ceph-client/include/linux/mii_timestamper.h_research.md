# sources/distributed-fs/ceph-client/include/linux/mii_timestamper.h

## Purpose
Defines callback interfaces and registration helpers for MII/PHY timestamping devices.

## Important APIs/Types
`struct mii_timestamper` supplies `rxtstamp`, `txtstamp`, `hwtstamp_set`, `hwtstamp_get`, `link_state`, `ts_info`, and owning `device`. `struct mii_timestamping_ctrl` supplies channel probe/release callbacks. Registration APIs are present when `CONFIG_NETWORK_PHY_TIMESTAMPING` is enabled; stubs return `-EOPNOTSUPP` or `NULL` otherwise.

## Control Flow
Drivers register controllers or timestampers. RX paths may defer accepted SKBs until timestamp delivery via `netif_rx()`. TX paths complete timestamps through `skb_complete_tx_timestamp()`. Ioctl/ethtool paths delegate to hardware timestamp callbacks.

## State And Persistence
Timestamping state lives in driver-private structures embedding `mii_timestamper`; hardware configuration persists after `hwtstamp_set`.

## Dependencies And Integration Points
Depends on device, ethtool, SKB, timestamping, and PHY types. Integrates with phylib, PTP classification, hardware timestamp ioctls, ethtool timestamp info, and device-tree channel lookup.

## Risks
SKB ownership mistakes, missing TX completions, violating PHY mutex expectations for `link_state`, and silent feature absence with the config disabled.

## Test Signals
Hardware timestamp set/get, ethtool timestamp info, RX/TX PTP timestamp delivery, link transitions, unregister cleanup, and CONFIG-disabled behavior.
