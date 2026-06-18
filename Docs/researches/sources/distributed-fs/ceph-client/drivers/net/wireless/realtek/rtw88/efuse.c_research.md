# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.c

## Purpose

`efuse.c` reads Realtek physical eFuse storage, reconstructs the logical eFuse map, and passes that logical map to chip-specific parsing code. eFuse data is the device's nonvolatile configuration source for MAC address, RF front-end information, regulatory/power characteristics, and hardware capability fields used during probe and bring-up.

## Important APIs, Types, and Functions

`rtw_parse_efuse_map()` is the main entry point. It allocates physical and logical maps using sizes already stored in `rtwdev->efuse`, dumps physical eFuse, reconstructs logical eFuse contents, then calls `chip->ops->read_efuse(rtwdev, log_map)` for chip-specific interpretation.

`rtw_read8_physical_efuse()` is exported for single-byte physical reads. It programs the address field in `REG_EFUSE_CTRL`, clears `BIT_EF_FLAG`, polls until the flag is set, and returns either the low data byte or `EFUSE_READ_FAIL` on timeout.

Internal helpers include `switch_efuse_bank()`, `rtw_dump_physical_efuse_map()`, and `rtw_dump_logical_efuse_map()`. The logical parser uses the local header macros to recognize 1-byte and 2-byte eFuse headers, block indexes, word-enable bits, and logical byte offsets.

## Control Flow

Physical dump flow first grants eFuse ownership through `rtw_chip_efuse_grant_on()`, selects the Wi-Fi eFuse bank, disables the chip 2.5V LDO through `chip->ops->cfg_ldo25(false)`, and loops over every physical byte. Each iteration writes the target address and a cleared flag into `REG_EFUSE_CTRL`, waits up to 1,000,000 microsecond-delay iterations for `BIT_EF_FLAG`, and stores the returned data byte. On success it releases the grant with `rtw_chip_efuse_grant_off()`.

Logical reconstruction walks physical bytes until the protected tail region or an invalid header. A 2-byte header is identified when the low five bits of the first header are `0xf`; otherwise a compact 1-byte header is used. For each enabled word, the parser copies two physical bytes into the logical map at `block_idx * 8 + word * 2`, validating both physical and logical bounds. The logical map is initialized to `0xff`, preserving unwritten eFuse semantics.

## State and Persistence

The eFuse itself is persistent hardware storage, but this file only reads it. Parsed values persist afterward in `rtwdev->efuse` and other fields populated by the chip-specific `read_efuse` operation. Temporary physical and logical maps are freed before return. The code changes transient hardware state by selecting the Wi-Fi bank, toggling eFuse grant, and disabling the 2.5V LDO during physical reads.

## Dependencies and Integration Points

This file depends on register definitions in `reg.h`, MMIO helpers from `hci.h`, chip operations for eFuse grant/LDO control/chip-specific parsing, and the size fields in `struct rtw_efuse`. It integrates early in device initialization, before many capability-dependent decisions in MAC, PHY, firmware, and regulatory paths.

## Risks

The physical dump has an important cleanup risk: if polling times out inside `rtw_dump_physical_efuse_map()`, the function returns `-EBUSY` before the final grant-off call. That can leave eFuse ownership state uncleared depending on lower-layer behavior. The parser also depends on correct `physical_size`, `protect_size`, and `logical_size`; bad values can reject maps or truncate valid data. Header handling treats `0xff` and selected extended-header forms as end-of-map, so corrupted physical eFuse can silently produce a mostly `0xff` logical map until chip parsing fails or yields defaults.

## Test Signals

Probe tests should confirm `rtw_parse_efuse_map()` succeeds on supported chips and logs failures for malformed maps. Unit-style parser tests can feed synthetic physical maps covering 1-byte headers, 2-byte headers, skipped words, invalid headers, logical overflow, and protected-tail boundaries. Hardware tests should verify eFuse grant is released after successful reads, single-byte reads return expected values, and chip-specific capability fields match known board data.
