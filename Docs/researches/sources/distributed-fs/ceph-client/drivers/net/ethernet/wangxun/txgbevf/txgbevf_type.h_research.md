# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/txgbevf_type.h

Purpose: defines constants for the Wangxun TXGBE virtual-function driver.

Important definitions: device IDs cover SP1000, WX1820, and AML VF variants. Capacity constants limit MSI-X vectors to 2, RSS and RX/TX queue counts to 4, and default descriptor rings to 128 entries each. Work limits default to 256 for both TX and RX.

Integration: `txgbevf_main.c` consumes these values for PCI matching, netdev allocation, queue sizing, interrupt capability, and ring/work defaults. The constants also define the VF driver's public hardware assumptions relative to shared `libwx` queue/interrupt helpers.

State and persistence: this header defines no runtime storage. It constrains runtime state allocated in `struct wx`.

Risks and tests: risk lies in stale device IDs or hardware capability limits that diverge from PF-advertised resources. Test signals include successful PCI matching for all IDs, correct queue count negotiation, descriptor setup under traffic, and module build coverage.
