# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/fw.c

## Purpose

`fw.c` parses and validates the carl9170 firmware image before the driver exposes hardware capabilities. It locates the descriptor block, validates descriptor chaining and CRCs, checks API and mandatory feature compatibility, copies firmware capability values into `ar->fw`, and updates mac80211/wiphy capability flags.

## Important APIs, Types, and Functions

The exported entry point is `carl9170_parse_firmware()`. Internal helpers include `carl9170_find_fw_desc()`, `carl9170_fw_verify_descs()`, `carl9170_fw_find_desc()`, `carl9170_fw_checksum()`, `valid_dma_addr()`, `valid_cpu_addr()`, `carl9170_fw_tx_sequence()`, `carl9170_fw_set_if_combinations()`, and `carl9170_fw()`.

## Control Flow

`carl9170_parse_firmware()` requires `ar->fw.fw`, finds the descriptor region, verifies that every descriptor length fits within the maximum descriptor area and terminates with a compatible `LAST` descriptor, stores `ar->fw.desc`, prints driver/firmware versions, and calls `carl9170_fw()`. `carl9170_fw()` checks CRCs, requires a compatible OTUS descriptor, API version 1, mandatory PHY/BAR/USB-init features, rejects `UNUSABLE` images, then enables optional feature-dependent driver capabilities.

## State and Persistence Behavior

The parser persists firmware-derived state in `ar->fw`: API version, miniboot offset, stream support, RX filter flags, counter and WoW support, VIF count, command buffers, firmware address, RX frame size, memory block count and size, beacon buffer address and length, and optional TX sequence table address. It also mutates `hw->extra_tx_headroom`, wiphy interface capabilities, wakeup enablement, `rx_filter_caps`, and `mem_free_blocks`.

## Dependencies and Integration Points

The file depends on Linux firmware loading, crc32, firmware descriptor definitions from `fwdesc.h`, command ABI constants from `fwcmd.h`, AR9170 memory map constants from `hw.h`, and mac80211/cfg80211 wiphy capability fields. Later USB, MAC, PHY, TX, RX, WoW, and interface code rely on the parsed `ar->fw` contract.

## Risks and Edge Cases

Descriptor scanning is byte-wise and accepts the first OTUS magic sequence that passes later validation. Images without `CHK` descriptors are accepted with a warning, reducing tamper detection. Feature bits beyond the driver's enum only warn. Incorrect firmware-provided sizes or addresses are rejected, which is critical because later code uses them for memory accounting and register writes.

## Test Signals

Test valid firmware, truncated descriptor areas, bad descriptor lengths, missing `LAST`, missing `OTUS`, bad CRCs, unsupported API versions, missing mandatory feature bits, `UNUSABLE` images, invalid memory sizes, and invalid firmware/beacon/TX-sequence addresses. Confirm wiphy interface modes and `ar->fw` fields match descriptor variants.
