# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/fwdesc.h

## Purpose

`fwdesc.h` defines the descriptor format embedded in carl9170 firmware images. It is the versioned metadata ABI used by `fw.c` to discover firmware features, memory layout, release information, checksums, debug addresses, TX sequence-table address, WoW support, and descriptor termination.

## Important APIs, Types, and Functions

`enum carl9170fw_feature_list` assigns stable feature bit positions. Descriptor magics include `OTUS`, `MOTD`, `FIX`, `DBG`, `CHK`, `TXSQ`, `WOL`, and `LAST`. `struct carl9170fw_desc_head` is the common header. Specialized descriptors include OTUS, MOTD, fix, debug, checksum, TX sequence, WoW, and last descriptors. Helpers include date packing/unpacking macros, fill helpers, descriptor iteration, support-bit testing, descriptor comparison, and firmware size checks.

## Control Flow

`fw.c` iterates descriptor headers with `carl9170fw_for_each_hdr()` until `LAST_MAGIC`, validates versions and lengths with `carl9170fw_desc_cmp()`, and then uses feature bits and descriptor payloads to configure the driver. The size-check helper gates firmware scan bounds before descriptor parsing begins.

## State and Persistence Behavior

The header itself stores no runtime state, but descriptor values become persistent per-device runtime state after parsing: firmware feature flags, firmware code address, beacon buffer bounds, miniboot offset, TX fragment size, RX maximum frame length, command buffers, API version, VIF count, release string, CRCs, debug counters, TX sequence table address, and WoW trigger support.

## Dependencies and Integration Points

The descriptor ABI is shared with the firmware build and the Linux driver. It depends on little-endian packed layout and the fixed feature bit order. `fw.c` relies on its version constants to decide compatibility; mac80211 capability advertisement and later command paths rely on parsed feature bits.

## Risks and Edge Cases

The version check accepts only descriptors whose min/current range includes the requested compatible revision; incorrect version constants can reject otherwise usable firmware. Descriptor iteration trusts sane lengths and must be paired with the stronger verifier in `fw.c`. `CARL9170FW_LAST_DESC_SIZE` is defined using the fix descriptor size and is part of the existing compatibility contract.

## Test Signals

Build firmware and driver with matching descriptor definitions. Validate descriptor parsing across minimum/current revisions, unknown future feature bits, missing optional descriptors, protected and unprotected images, and boundary firmware sizes. Static checks should preserve feature enum order and packed descriptor sizes.
