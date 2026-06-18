# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Kconfig

Purpose: Defines configuration for legacy Intel PRO/Wireless 2100/2200 drivers and their deprecated shared `LIBIPW` stack.

Important APIs/configs: `IPW2100` and `IPW2200` are tristate PCI/CFG80211 drivers selecting Wireless Extensions, private WEXT, firmware loader, and `LIBIPW`. Optional booleans enable monitor/promiscuous/radiotap/QoS/debug features. `LIBIPW` selects crypto, ARC4, and CRC32, while `LIBIPW_DEBUG` enables extra debug output.

Control flow and state: Kconfig dependency flow controls feature visibility and selected support libraries. Help text documents firmware requirements, module-vs-built-in tradeoffs, debug interfaces, and monitor/radiotap behavior.

Dependencies and integration: Depends on PCI and CFG80211, integrates with firmware loading, WEXT compatibility, crypto, and deprecated libipw code. Risks include built-in drivers probing before firmware is accessible, legacy WEXT interfaces, deprecated stack maintenance, typo-like example debug value, and feature combinations that expose monitor interfaces unable to transmit. Test signals include Kconfig dependency resolution, module and built-in firmware scenarios, monitor/radiotap interface creation, QoS builds, and debug sysfs/proc controls.
