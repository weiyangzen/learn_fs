## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.h

Purpose: ethtool declarations and constants for Atlantic.

Important APIs/types: declares `extern const struct ethtool_ops aq_ethtool_ops`, defines private flag mask as Atlantic hardware loopback flags, and provides SFF-8472 I2C device/register constants used for optical module EEPROM detection and reads.

Control flow: none.

State and persistence: constants only.

Dependencies/integration: included by `aq_main.c` to attach ethtool ops and by `aq_ethtool.c` for EEPROM and private flag definitions.

Risks: private flag mask must track `aq_hw.h` loopback bit definitions. EEPROM constants must remain correct for SFF-8079/SFF-8472 module interpretation.

Test signals: compile, `ethtool --show-priv-flags`, loopback flag changes, and module info/eeprom reads.
