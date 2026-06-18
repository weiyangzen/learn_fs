# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mac.c

Purpose: Programs Sunplus switch/MAC hardware registers for port enablement, descriptor base addresses, flow/VLAN policies, MAC address table entries, multicast/promiscuous filtering, initialization, and soft reset.

Important APIs/functions: `spl2sw_mac_hw_init()` writes descriptor base addresses, flow-control thresholds, LED polarity, CPU/port learning behavior, forced RMII mode, PVID/VLAN membership, storm/RMC policy, and default interrupt mask. `spl2sw_mac_hw_start()` enables CPU port 0, CRC padding, and currently enabled LAN ports. `spl2sw_mac_hw_stop()` masks/clears interrupts and disables CPU ports when no netdev is enabled, then disables inactive LAN ports. `spl2sw_mac_addr_add()` and `spl2sw_mac_addr_del()` write MAC table entries and poll for completion. `spl2sw_mac_rx_mode_set()` maps netdev promiscuous/allmulti/multicast state onto CPU forwarding disable bits. `spl2sw_mac_soft_reset()` stops hardware, flushes RX descriptors, resets ring indices, reinitializes registers, and restarts.

Control flow and state: Hardware state persists in MMIO registers and the switch address table. `comm->enable` drives port-disable bits. VLAN group 0 maps CPU0+port0, and group 1 maps CPU0+port1, matching per-netdev `to_vlan` and `vlan_id`. The implementation relies on `FIELD_PREP()` with port bitmasks for multi-bit fields.

Dependencies and integration points: Called by probe, open/stop, set-rx-mode, set-MAC-address, and TX timeout paths. Depends on descriptor DMA addresses already being allocated and on register/bit definitions from `spl2sw_register.h`/`spl2sw_define.h`.

Risks and test signals: Several clear operations use `reg &= FIELD_PREP(mask, ~comm->enable) | ~mask`, so bitfield behavior with inverted small port masks is delicate. MAC table add/delete timeouts are short and hardware-dependent. Test per-port VLAN isolation, MAC address changes, promisc/allmulti/multicast transitions, open/stop one port while preserving the other, soft reset under TX load, and link speed/duplex changes after reset.
