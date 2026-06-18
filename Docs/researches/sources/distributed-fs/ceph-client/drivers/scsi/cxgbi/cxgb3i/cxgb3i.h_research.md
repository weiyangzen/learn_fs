# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.h

## Purpose

This header provides T3-specific constants, exported CPL handler declaration, netdev-private IPv4 accessors, and no-RSS CPL layout structures used by `cxgb3i.c`.

## Important APIs, Types, And Functions

Constants include `CXGB3I_SCSI_HOST_QDEPTH`, `CXGB3I_MAX_LUN`, `ISCSI_PDU_NONPAYLOAD_MAX`, and `CXGB3I_TX_HEADER_LEN`. The header declares `cxgb3i_cpl_handlers[NUM_CPL_CMDS]`. Inline helpers `cxgb3i_get_private_ipv4addr()` and `cxgb3i_set_private_ipv4addr()` read/write `struct port_info` iSCSI fields. `struct cpl_iscsi_hdr_norss` and `struct cpl_rx_data_ddp_norss` model compact receive-side CPL data without RSS prefix.

## Control Flow

`cxgb3i.c` uses the constants in host-template and skb reservation setup, registers the exported handler array with cxgb3, and calls the IPv4 helpers during HBA address synchronization. Receive parsing copies no-RSS CPL trailers into the local structs to extract PDU length, sequence, digest, and DDP status.

## State And Persistence

The header itself has no state. The IPv4 accessors mutate `port_info.iscsic.flags`, `port_info.iscsi_ipv4addr`, and `iscsic.mac_addr` in the cxgb3 netdev private area. That state persists for the life of the netdev/adapter and is used by offloaded connection setup.

## Dependencies And Integration Points

It depends on cxgb3 `struct port_info`, CPL types, iSCSI header/digest constants, skb header sizes, and `NUM_CPL_CMDS`. It is the T3-specific bridge between cxgb3 network internals and the shared cxgbi iSCSI layer.

## Risks

The inline helpers assume `netdev_priv(ndev)` is a cxgb3 `struct port_info`; using them with another netdev type corrupts memory. `CXGB3I_TX_HEADER_LEN` must match the headroom required by `make_tx_data_wr()`. The no-RSS CPL structs must match firmware layout exactly or RX parsing in `do_iscsi_hdr()` misinterprets status and lengths.

## Test Signals

Build tests should catch missing cxgb3 types. Runtime tests include private IPv4 propagation to physical and VLAN devices, TX skb headroom checks, and RX PDU parsing with DDP and non-DDP payloads.
