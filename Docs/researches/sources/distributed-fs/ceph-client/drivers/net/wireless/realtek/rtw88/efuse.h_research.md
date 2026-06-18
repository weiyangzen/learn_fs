# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.h

## Purpose

`efuse.h` declares the public eFuse read interface and bitfield helpers for extracting hardware capability values from the logical eFuse map. It is the shared contract between generic eFuse dumping and chip-specific eFuse parsers.

## Important APIs, Types, and Functions

The file defines hardware capability constants such as `EFUSE_HW_CAP_PTCL_VHT`, supported bandwidth bit positions, and `EFUSE_READ_FAIL`. The `GET_EFUSE_HW_CAP_*` macros extract HCI type, bandwidth support, NSS, antenna number, and protocol fields from a little-endian capability blob using `le32_get_bits()`.

It declares `rtw_parse_efuse_map()` and exported `rtw_read8_physical_efuse()`.

## Control Flow

The header has no runtime flow. It supplies macros used by parsers after `efuse.c` reconstructs the logical eFuse map.

## State and Persistence

The macros read caller-provided eFuse buffers and do not mutate state. The declarations refer to functions that populate persistent `rtwdev->efuse` state during initialization.

## Dependencies and Integration Points

Consumers must pass correctly aligned and sufficiently large hardware capability buffers because the macros cast to `__le32 *` and index word 1. The header integrates with chip-specific `read_efuse` implementations, HCI selection, PHY capability setup, and feature advertisement.

## Risks

The capability macros assume the buffer layout is valid for the target chip. Using them on a shorter or differently formatted map can read the wrong word and misconfigure HCI, NSS, antennas, or protocol capabilities. Any new chip family with a different eFuse capability layout needs separate parsing rather than blindly reusing these helpers.

## Test Signals

Tests should compare parsed HCI/BW/NSS/antenna/protocol values against known eFuse dumps for each chip family. Build tests should cover endian helpers and ensure all users include the required bitops/endian definitions through their include chain.
