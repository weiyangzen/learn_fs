<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c

Purpose: implements the B0/B1 Atlantic hardware operation table and capability records, adding richer offloads, TC/QoS, PTP, VLAN filters, temperature, and module EEPROM access beyond A0.

Important APIs/functions: exports B0 capability constants and `hw_atl_ops_b0`; selected helper functions are also declared in the header for reuse. Major functions cover reset, flow control, QoS/PTP TC reservation, RSS, offload setup, TC rate limiting, TX/RX path init, MAC, hardware init/start/stop, descriptor TX/RX, hardware timestamp RX, IRQ moderation, filters, VLAN control, loopback, PTP clock/frequency/GPIO/timestamp conversion, MAC temperature, SMBus module EEPROM reads, and stats/regs/fw version via utils.

Control flow: init programs TX/RX paths, MAC, firmware link/MPI state, QoS, RSS, PCI/MRRS workarounds, interrupt maps including optional link IRQ, and offloads. TX xmit emits context descriptors for GSO and VLAN before data descriptors. RX receive parses checksum, VLAN, RSS, LRO/jumbo chains, errors, and lengths. PTP ops expose PHC read/adjust, firmware frequency requests, GPIO pulse control, external timestamp PHY registers, RX timestamp trailers, and HWTS writebacks.

State and persistence: programs MMIO, firmware requests, PHY registers, `ptp_clk_offset`, descriptor rings, VLAN/L2/L3/L4 filters, IRQ moderation, and SMBus controller state. Runtime state is in `aq_hw_s`, configs, and rings.

Dependencies and integration: used by PCI board table for B0/B1 devices; depends on generic NIC/ring/PHY, low-level LLH registers, firmware request structures, and PTP/filter contracts.

Risks: rate-limit math depends on link speed and TC masks; PTP frequency adjustment uses fixed MAC/PHY counter constants; VLAN promisc behavior is deliberately forced in some modes; SMBus operations must always stop transfers on error; RX head validation protects against bogus hardware values. Test signals include B0 probe, TSO/TSO6/GSO UDP, VLAN strip/insert/filter, LRO, mqprio min/max rates, PTP PHC/GPIO/timestamps, loopback, module EEPROM reads, thermal reads, and interrupt moderation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.c -->
