## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_stats.h

### Purpose
Declares generic Cisco vNIC transmit and receive statistic layouts. SNIC is a SCSI-over-vNIC driver but reuses common vNIC hardware statistics, including Ethernet-like counters for frames, bytes, drops, errors, RSS, CRC, and packet-size buckets.

### Important APIs, Types, and Constants
- `struct vnic_tx_stats` includes successful frame and byte counters split by unicast/multicast/broadcast, plus drops, errors, TSO, and reserved expansion slots.
- `struct vnic_rx_stats` includes successful and total frames, byte counters, drops/no-buffer/error counters, RSS/CRC counters, frame-size buckets, and reserved expansion slots.
- `struct vnic_stats` groups TX and RX stats.

### Control Flow and State
There is no control flow. These are persistent hardware/firmware-facing counters, typically fetched or exposed through driver diagnostics. Reserved fields preserve ABI room for future counters.

### Dependencies and Integration Points
The file depends on fixed-width kernel integer types. It integrates with SNIC/vNIC stats retrieval and debug paths, not with the SCSI command path directly.

### Risks and Test Signals
The ABI risk is layout drift or width mismatch against firmware. Test signals include stable counter reads under traffic, no wrap handling assumptions beyond `u64`, and debugfs/sysfs/ethtool-style consumers reading expected offsets.
