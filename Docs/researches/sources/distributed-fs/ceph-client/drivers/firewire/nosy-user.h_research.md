<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h

Purpose: defines the small userspace ABI for the `nosy` FireWire snoop-mode character device. It gives user programs the ioctl numbers, statistics structure, and packet layout expected from `nosy.c`.

Important APIs and control flow: `NOSY_IOC_GET_STATS` copies out `struct nosy_stats`; `NOSY_IOC_START` adds the client to the active capture list; `NOSY_IOC_STOP` removes it; and `NOSY_IOC_FILTER` writes a 32-bit tcode mask. `struct nosy_stats` reports total packets offered to a client buffer and packets dropped because that buffer was full. The comment documents read records as a CPU-endian microsecond timestamp quadlet, little-endian quadlet-padded packet data, and a little-endian ack quadlet.

State and persistence behavior: this header contains no mutable state. Its definitions are persistent ABI: ioctl numbers and record layout must remain compatible with existing `nosy-dump` style tools.

Dependencies and integration points: depends on Linux ioctl encoding and fixed-width UAPI types. It is included by `nosy.c` and by userspace tools built against this kernel header.

Risks and test signals: `NOSY_IOC_STOP` and `NOSY_IOC_FILTER` both use command number 2 with different direction bits, so tooling should use the macros rather than raw numbers. The packet layout mixes CPU-endian timestamp with little-endian packet words, requiring explicit userspace parsing. Test signals include successful ioctl decoding from userspace, stats increasing during capture, filter masks suppressing unwanted tcodes, and readers correctly handling bus-reset timestamp-only records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/nosy-user.h -->
