# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.h

## Purpose

`nfp_net_ctrl.h` defines the firmware-facing control BAR ABI for NFP network vNICs. It is the central map of offsets, bit definitions, mailbox commands, metadata formats, RSS layout, ring configuration registers, statistics registers, TLV capability records, and parsed TLV capability state used by the rest of the NFP network driver.

## Important APIs, Types, and Functions

The file exports constants rather than executable code. Important groups include `NFP_NET_CFG_CTRL*` capability/control bits, `NFP_NET_CFG_UPDATE*` reconfiguration flags, `NFP_NET_CFG_STS*` link status and link-rate encodings, RSS controls under `NFP_NET_CFG_RSS_*`, TX/RX ring register address macros, interrupt-cause registers, legacy and TLV statistics offsets, mailbox command IDs, and BPF/IPsec/flow-steering metadata constants. `struct nfp_net_tlv_caps` is the parsed TLV state consumed by runtime code, and `nfp_net_tlv_caps_parse()` is the parser entry point implemented elsewhere.

## Control Flow

There is no local control flow, but the definitions shape driver sequencing. Runtime code writes control bits, ring DMA addresses, ring sizes, MSI-X vectors, mailbox payloads, and RSS tables into the CFG BAR, then signals firmware with the matching `NFP_NET_CFG_UPDATE_*` bits. Consumers also read status/capability words and optional TLVs to choose datapath features, representor capabilities, mailbox location, per-vNIC statistics layout, crypto capabilities, and ME clock frequency for interrupt moderation conversion.

## State and Persistence Behavior

The state described here lives in device BAR memory and firmware-owned control structures, not in this header. Persistent hardware-facing fields include enabled ring masks, MTU, buffer size, MAC address, RSS key/indir table, ring DMA locations, IRQ moderation values, stats counters, mailbox values, and TLV capability data. Because offsets are an ABI, changes are high risk and must remain compatible with firmware.

## Dependencies and Integration Points

The header is included by PF/VF probe, datapath setup, ethtool, representor, SR-IOV, XDP/BPF, flow-steering, crypto, and debug paths. It depends only on Linux integer/bit macros but integrates with firmware symbols, NFP queue-controller BARs, ethtool link-rate reporting, devlink shared-buffer state, and mailbox helpers.

## Risks and Edge Cases

Offset and bit definitions are contract-sensitive. Incorrect sizes or alignment for TLVs, mailbox values, ring blocks, or stats blocks can make the host and firmware disagree. Some features have mutually constrained control bits, such as old/new VLAN offloads, LSO/LSO2, RSS/RSS2, checksum-complete metadata, and representor capabilities. TLV parsing must reject required unknown TLVs while tolerating reserved/padding regions. Code using mailbox length macros must respect `NFP_NET_CFG_MBOX_VAL_MAX_SZ`.

## Test Signals

Useful coverage is primarily integration and ABI validation: PF/VF probe across firmware ABI versions, ethtool stats with legacy and TLV stats, RSS programming, VLAN strip/insert variants, mailbox VF/VLAN/multicast/flow-steer commands, interrupt moderation, BPF/crypto capability parsing, and register dumps verifying offsets against firmware documentation.
