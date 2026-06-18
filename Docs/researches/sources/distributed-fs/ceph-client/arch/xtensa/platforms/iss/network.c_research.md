# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/network.c

Purpose: Implements ISS virtual Ethernet devices backed by host tuntap interfaces through simulator simcalls.

Important APIs, types, and functions: `struct iss_net_private`, `struct iss_net_ops`, `tuntap_probe/open/close/read/write/poll`, `iss_net_rx()`, `iss_net_poll()`, `iss_net_open()`, `iss_net_close()`, `iss_net_start_xmit()`, `iss_net_configure()`, `iss_net_setup()`, and `iss_net_init()`.

Control flow: Early `ethX=` command-line parsing records requested devices in a memblock list. Device init allocates `net_device`, parses `tuntap,[mac],dev`, registers a platform device and netdev. Open attaches host `/dev/net/tun`, drains pending RX, and starts a poll timer. RX polls host fd, allocates skb, reads packet, sets protocol, updates stats, and injects with `netif_rx()`. TX writes skb data to host fd and updates stats.

State and persistence: Maintains per-device host fd, timers, net stats under spinlock, platform device, and command-line init list.

Dependencies and integration: Linux netdev/platform/timer APIs, host TUN/TAP via simcall open/ioctl/read/write/poll, command-line `__setup`, and MAC address helpers.

Risks: Polling rather than interrupts limits performance; MTU changes are rejected; host read errors close the device; command-line parser mutates strings and uses memblock allocations; simcall backend must support ioctl/select/open.

Test signals: Boot with `eth0=tuntap,<mac>,tap0`, interface registration, ping/DHCP on host tap, RX/TX stats, invalid MAC/device args, host fd failure, and close/reopen.
