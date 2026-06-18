# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pwrseqcmd.h

## Purpose
Defines the compact Realtek power-sequence command format and declares `rtl_hal_pwrseqcmdparsing()`.

## Important APIs, Types, And Functions
Commands are READ, WRITE, POLLING, DELAY, and END. Base selectors are MAC, USB, PCIE, and SDIO. Masks select interface, fab vendor, and chip cut. `struct wlan_pwr_cfg` packs offset, cut, fab, interface, base, command, mask, and value; getter macros expose fields.

## Control Flow
Chip power arrays are filtered by cut/fab/interface. Matching commands perform masked register writes, polls, delays, or termination.

## State And Persistence
No header-owned state; parsed commands mutate hardware registers.

## Dependencies And Integration Points
Includes `wifi.h` and is consumed by chip-specific power sequences with parser implementation in `core.c`.

## Risks
Arrays must be terminated by END. Bitfield packing is ABI sensitive. Polling uses fixed limits and can fail slowly with bad masks.

## Test Signals
Power-on/off arrays for PCI/USB/SDIO, register write/poll success, delay units, and malformed/no-match command review.
