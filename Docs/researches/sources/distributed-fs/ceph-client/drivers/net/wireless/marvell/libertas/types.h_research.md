# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/types.h

## Purpose
Defines IEEE and Marvell TLV structures shared by Libertas command construction and parsing, including scan/channel TLVs, domain/power/auth TLVs, LED TLVs, and proprietary mesh information elements.

## Important Types And Constants
Core types include `struct ieee_ie_header`, CF/IBSS/FH/DS parameter sets, `struct mrvl_ie_header`, flexible-array TLV payload structs, channel scan parameter sets, RSSI/SNR threshold TLVs, beacon/probe TLVs, LED GPIO/behavior TLVs, `struct mrvl_meshie_val`, `struct mrvl_meshie`, and `struct mrvl_mesh_defaults`. Constants define standard and proprietary TLV ids, including `TLV_TYPE_MESH_ID` and `TLV_TYPE_OLD_MESH_ID`.

## Control Flow And State
No executable code. These packed structs shape variable-length command buffers for scan, 11d, authentication, events, LED configuration, and mesh persistent configuration.

## Dependencies And Integration
Included by `host.h` and other Libertas files. Depends on Linux Ethernet and IEEE 802.11 definitions and explicit endian annotations.

## Risks And Test Signals
Risks include flexible-array sizing mistakes, endian mistakes, mesh IE length mismatch, and inconsistent TLV ids across firmware revisions. Test signals include scan request/response parsing, country/domain programming, event subscription TLVs, LED commands, and mesh persistent IE reads/writes.
