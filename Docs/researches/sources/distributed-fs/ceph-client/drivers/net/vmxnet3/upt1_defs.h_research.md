# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/upt1_defs.h

## Purpose
Defines common UPT v1 structures and constants consumed by the vmxnet3 driver/device ABI. It describes per-queue TX/RX hardware statistics, interrupt moderation levels, RSS configuration format, and feature flags shared with the vmxnet3 descriptor/shared-memory definitions.

## Important APIs, Types, And Functions
`struct UPT1_TxStats` contains 64-bit counters for post-segmentation TSO packets/bytes, unicast/multicast/broadcast packets and bytes, TX errors, and TX discards. `struct UPT1_RxStats` mirrors RX-side counters with LRO packets/bytes, pre-LRO unicast/multicast/broadcast packets and bytes, out-of-buffer events, and RX errors.

Interrupt moderation constants define `UPT1_IML_NONE`, `UPT1_IML_HIGHEST`, and `UPT1_IML_ADAPTIVE`. RSS constants define supported hash type bits for IPv4, TCP/IPv4, IPv6, and TCP/IPv6, and hash functions including Toeplitz. `struct UPT1_RSSConf` holds `hashType`, `hashFunc`, key/table sizes, a 40-byte hash key, and a 128-entry indirection table.

Feature flags are little-endian 64-bit values: RX checksum verification, RSS, VLAN tag stripping, LRO, and inner checksum offload for Geneve/VXLAN-like encapsulation. The use of `cpu_to_le64()` makes these constants suitable for device-shared little-endian feature fields rather than host-native bit arithmetic.

## Control Flow
There is no executable control flow. The vmxnet3 driver includes this header through `vmxnet3_defs.h`, embeds `UPT1_TxStats` and `UPT1_RxStats` in queue descriptors, and writes/reads RSS and feature fields as part of device configuration and stats retrieval.

## State And Persistence Behavior
The structures define shared-memory state exchanged between driver and device. Queue stats are populated by the device and read by the driver after stats/status commands. RSS configuration and feature bits are driver-provided configuration state. There is no standalone persistence; values survive only while the vmxnet3 device instance and shared memory allocations remain valid.

## Dependencies And Integration Points
Depends on kernel integer typedefs (`u8`, `u16`, `u64`) and endian helpers. It is included by `vmxnet3_defs.h`, where UPT stats become part of `Vmxnet3_TxQueueDesc` and `Vmxnet3_RxQueueDesc`, and UPT feature flags feed `Vmxnet3_MiscConf.uptFeatures`. It is an ABI boundary with VMware virtual hardware, so layout and sizes matter.

## Risks
Changing field order, field width, constants, or endian treatment can break driver/device compatibility. Stats counters are plain 64-bit shared fields, so readers must account for device update timing and endian/atomicity expectations in the consuming code. The RSS table and key size limits are fixed; callers must not overrun the arrays or advertise unsupported sizes.

## Test Signals
Build testing should catch missing typedef/endian dependencies. Runtime signals include correct ethtool statistics for vmxnet3 queues, successful RSS configuration with expected hash distribution, interrupt moderation behavior matching selected levels, VLAN/RX checksum/LRO feature negotiation, and compatibility across vmxnet3 device revisions that consume the UPT v1 ABI.
