# sources/distributed-fs/ceph-client/include/linux/mmc/sd.h

## Purpose
`mmc/sd.h` defines SD memory-card protocol constants distinct from native MMC. It covers SD command opcodes, application commands, OCR bits, switch argument layout, interface-condition layout, SCR versions, bus widths, switch modes, access modes, and erase/discard arguments.

## Important APIs, Types, And Functions
Important constants include `SD_SEND_RELATIVE_ADDR`, `SD_SEND_IF_COND`, `SD_SWITCH_VOLTAGE`, `SD_ADDR_EXT`, `SD_SWITCH`, erase block commands, ACMD bus/status/OCR/SCR commands, extension read/write commands, OCR capability bits (`SD_OCR_S18R`, `SD_OCR_2T`, `SD_OCR_XPC`, `SD_OCR_CCS`), SCR spec versions, `SD_BUS_WIDTH_1`, `SD_BUS_WIDTH_4`, `SD_SWITCH_CHECK`, `SD_SWITCH_SET`, `SD_SWITCH_GRP_ACCESS`, `SD_SWITCH_ACCESS_HS`, `SD_ERASE_ARG`, and `SD_DISCARD_ARG`.

## Control Flow And State
The header stores no state. Core SD enumeration uses these constants to probe voltage and capacity, issue application commands after `APP_CMD`, switch speed modes, configure bus width, read status/SCR data, and set erase or discard command arguments. SDUC address extension support is represented by `SD_ADDR_EXT`.

## Dependencies And Integration Points
It has no includes and integrates with MMC command construction in `core.h`, SD card parsing in `card.h`, host voltage switching in `host.h`, and block erase/discard paths.

## Risks And Test Signals
Risks include MMC/SD opcode confusion, wrong OCR capability handling during voltage switch, bad switch function group encoding, SDHC/SDXC/SDUC capacity/addressing mistakes, and discard-vs-erase argument confusion. Test signals include SD card enumeration at multiple spec levels, 1.8 V switch tests, bus-width switching, high-speed switch tests, SCR/status parsing, and erase/discard command tests.
