# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_config.h

## Purpose
This header defines VF driver queue, interrupt, MTU, and configuration defaults plus accessor macros and config structures used by chip-specific setup and generic VF queue code.

## Important APIs, Types, And Functions
- Defaults: `OCTEP_VF_IQ_MAX_DESCRIPTORS`, `OCTEP_VF_OQ_MAX_DESCRIPTORS`, `OCTEP_VF_DB_MIN`, `OCTEP_VF_OQ_BUF_SIZE`, `OCTEP_VF_OQ_REFILL_THRESHOLD`, OQ interrupt thresholds, `OCTEP_VF_WAKE_QUEUE_THRESHOLD`, and MTU bounds.
- Accessors: `CFG_GET_IQ_*`, `CFG_GET_OQ_*`, `CFG_GET_PORTS_*`, and `CFG_GET_IOQ_MSIX()`.
- Structures: `struct octep_vf_iq_config`, `struct octep_vf_oq_config`, `struct octep_vf_ring_config`, `struct octep_vf_msix_config`, and `struct octep_vf_config`.

## Control Flow
Chip-specific VF setup initializes an allocated `struct octep_vf_config` with these defaults after reading hardware ring count. Generic queue setup uses the macros to allocate descriptor rings, choose thresholds, program interrupt moderation, and set real queue counts.

## State And Persistence
The header only defines structures. Runtime instances are held in `octep_vf_device->conf`; values are recreated at probe and are not persisted. Some config fields are then reflected into hardware registers during open.

## Dependencies And Integration Points
The header depends on kernel Ethernet and skb buffer-size concepts through source context. It is included by VF main, chip-specific hardware files, mailbox, Tx/Rx queue helpers, and ethtool code.

## Risks And Edge Cases
- Queue descriptor counts are assumed to work with ring masks and should remain powers of two.
- `OCTEP_VF_OQ_BUF_SIZE` uses page-sized skb overhead; architecture page-size differences can change receive buffer behavior.
- `OCTEP_VF_MAX_MTU` is fixed at 10000-byte frame size minus Ethernet header/FCS, while PF may report a different max through mailbox for PF-side MTU.
- `CFG_GET_IQ_INSTR_SIZE()` always returns 64, so 32-byte instruction support is nominal but not active.

## Test Signals
Compile all VF files, verify config initialization for CN9K and CNXK, run queue allocation at discovered ring counts, validate MTU min/max behavior, test OQ refill and interrupt moderation thresholds, and inspect ethtool channel counts.
