
# sources/distributed-fs/ceph-client/include/linux/oa_tc6.h

Purpose: declares the OPEN Alliance 10BASE-T1x MAC-PHY Serial Interface framework used by SPI-connected Ethernet MAC-PHY devices.

Important APIs/types/functions: `struct oa_tc6` is opaque framework state. `oa_tc6_init()` binds an SPI device and net device, `oa_tc6_exit()` tears it down, register helpers read/write one or multiple 32-bit registers, `oa_tc6_start_xmit()` transmits an skb through the TC6 data path, and `oa_tc6_zero_align_receive_frame_enable()` enables zero-alignment receive-frame behavior.

Control flow: an Ethernet MAC-PHY driver initializes TC6 with its SPI and netdev objects, uses register helpers for device setup, routes netdev transmit through `oa_tc6_start_xmit()`, enables optional receive alignment behavior, and calls exit during remove.

State and persistence: framework state is runtime SPI/netdev coordination state; hardware register values persist only according to device reset/power behavior. Packet buffers are transient.

Dependencies and integration points: depends on Ethernet netdev/skb types and SPI device APIs. It integrates SPI MAC-PHY drivers with the networking stack and OPEN Alliance TC6 register/data protocol implementation.

Risks and test signals: risks include SPI transfer framing errors, register burst length mistakes, netdev lifetime races, skb ownership errors, and receive alignment mismatches. Test signals include link bring-up on TC6 hardware, register read/write round trips, TX/RX packet tests, remove while traffic is active, and error injection for SPI failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oa_tc6.h -->
