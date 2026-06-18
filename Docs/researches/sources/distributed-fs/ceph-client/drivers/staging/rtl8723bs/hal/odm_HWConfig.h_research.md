# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_HWConfig.h

## Purpose

`odm_HWConfig.h` declares the raw RTL8723B PHY status report layout and ODM hardware configuration APIs. The source was read as a complete 86-line file.

## Important APIs, Types, and Functions

It defines bitfield `struct phy_rx_agc_info_t`, raw report `struct phy_status_rpt_8192cd_t`, and prototypes for `odm_phy_status_query`, RF/BB/FW config dispatchers, and `odm_signal_scale_mapping`.

## Control Flow

There is no executable flow; it provides ABI-like layout and function declarations.

## State and Persistence Behavior

The report structs describe transient RX descriptor/PHY-status bytes. Parsed results are stored elsewhere in `odm_phy_info`, station RSSI stats, and `dm_odm_t`.

## Dependencies and Integration Points

It depends on ODM endian macros and `dm_odm_t` definitions. It integrates raw receive status from the hardware RX path with ODM parsing.

## Risks and Edge Cases

The bitfield layout depends on `ODM_ENDIAN_TYPE`; incorrect endian detection corrupts AGC and antenna fields. Struct layout must match firmware/hardware RX status bytes exactly.

## Test Signals

Build checks on little-endian and layout/offset tests against known PHY status samples are the key signals.
