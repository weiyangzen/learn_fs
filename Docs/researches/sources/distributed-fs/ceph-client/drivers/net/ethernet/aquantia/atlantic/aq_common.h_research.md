## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_common.h

Purpose: common include hub and shared identifiers for Atlantic devices.

Important APIs/types: includes Ethernet, PCI, VLAN, `aq_cfg.h`, and utility definitions. Defines Aquantia PCI vendor ID, many AQtion device IDs, display NIC name, hardware revision selectors, and link speed/EEE bit masks.

Control flow: no executable logic.

State and persistence: constants only.

Dependencies/integration: included from most Atlantic files. Device IDs are used by PCI matching elsewhere; rate masks feed link settings, EEE ethtool conversion, and firmware configuration.

Risks: incorrect device IDs break probe matching. Speed bit changes must remain consistent with firmware and ethtool mapping. EEE mask composition is consumed directly by `aq_ethtool.c`.

Test signals: PCI ID table coverage, link speed advertisement tests, EEE get/set tests, and compile coverage across all Atlantic objects.
