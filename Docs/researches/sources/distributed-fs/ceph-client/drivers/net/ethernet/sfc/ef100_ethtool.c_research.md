<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c

## Purpose
Defines EF100-specific ethtool operations, mostly by wiring common SFC ethtool helpers to an EF100 netdevice and adding EF100 descriptor-ring size reporting.

## Important APIs, Types, And Functions
- `EFX_EF100_MAX_DMAQ_SIZE` sets the advertised maximum RX/TX ring size to 16384 descriptors.
- `ef100_ethtool_get_ringparam()` reports current `efx->rxq_entries` and `efx->txq_entries` plus EF100 max queue sizes.
- `const struct ethtool_ops ef100_ethtool_ops` publishes driver info, message level, pause, link settings, selftest, string/stat, RX NFC, reset, RSS context, module EEPROM, FEC, and ring parameter handlers.

## Control Flow
The netdev registration code assigns `net_dev->ethtool_ops = &ef100_ethtool_ops`. User ethtool requests then enter either the small EF100 ringparam helper or common SFC helpers. This file does not implement setters for ring size; it only exposes current and maximum values.

## State And Persistence
No private state is allocated. Reported state comes from the live `efx_nic` embedded behind the netdevice. Changes made by common ethtool operations, such as pause, FEC, RSS context, reset, or link settings, are handled by shared SFC code and/or firmware, not cached here.

## Dependencies And Integration Points
Depends on Linux ethtool/netdevice APIs, `efx_netdev_priv()`, common ethtool helpers in `ethtool_common.h`, MCDI port helpers, RSS context private sizing, and EF100 netdev registration. It is the user-space observability/control surface for EF100 netdevices.

## Risks And Edge Cases
The max ring size is a static QDMA hardware limit; actual allocation may be lower due to VI/channel constraints elsewhere. Because ringparam has no EF100 setter here, user expectations for resizing depend on common behavior and may differ from reported maxima. RSS context operations rely on shared code correctly interpreting EF100 capabilities.

## Test Signals
Run `ethtool -i`, `ethtool -g`, `ethtool -S`, `ethtool -k`, RSS indirection/key commands, FEC get/set, module EEPROM reads, selftests, and reset commands on an EF100 netdevice. Correct ringparam output should show max 16384 and current queue sizes from the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c -->
