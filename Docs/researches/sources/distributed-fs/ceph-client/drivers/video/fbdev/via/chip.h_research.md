# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/chip.h

## Purpose
`chip.h` defines VIA Unichrome chip IDs, revisions, transmitter IDs, bus/interface constants, and shared information structures that describe graphics, TMDS, LVDS, and pad-driving configuration.

## Important APIs, Types, And Data
Key constants include the VIA PCI vendor ID, `UNICHROME_*` chip names and PCI device IDs, CLE266/CX700 revisions, TMDS/LVDS transmitter IDs and I2C addresses, and data-width flags. Core structures are `tmds_chip_information`, `lvds_chip_information`, `enum via_2d_engine`, `chip_information`, `tmds_setting_information`, `lvds_setting_information`, `GFX_DPA_SETTING`, and `VT1636_DPA_SETTING`.

## Control Flow
This header has no executable control flow. `hw.c`, `dvi.c`, `lcd.c`, and acceleration setup use its constants to branch by chip family and fill shared configuration structs.

## State And Persistence
The structure definitions shape persistent runtime state stored in `viaparinfo->chip_info` and related setting pointers. The header itself does not allocate state.

## Dependencies And Integration Points
It includes `global.h`, which makes this a cyclic-looking but established local include relationship. Its structures are central integration points between chip probing, DVI/LVDS detection, mode setting, acceleration selection, and pad-drive tuning.

## Risks
The header is a single source of truth for many hardware IDs. A wrong ID or output-interface interpretation will route mode programming to the wrong registers. The include of `global.h` from `chip.h` increases coupling and makes isolated reuse difficult. Several structures use `int` for hardware enums rather than strongly typed enums, so invalid values can flow until checked in register-writing code.

## Test Signals
Signals include correct chip-family detection, expected 2D engine enum selection, successful TMDS/LVDS identification using declared I2C addresses, and build coverage for all files that consume `chip_information`.
